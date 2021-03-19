import reprlib
from enum import Enum
from itertools import chain

from library.infrastructure_architecture.event_sourced_architecture.abstract_event_store import AbstractEventStore
from utilities.time import monotonic_utc_now


class UnitOfWorkError(Exception):

    def __init__(self, message, events=None):
        super().__init__(message)
        self._events = events

    @property
    def events(self):
        return self._events

    def __repr__(self):
        return "{}({}, events={})".format(
            self.__class__.__name__,
            str(self),
            reprlib.repr(self._events)
        )


class ConflictError(UnitOfWorkError):
    pass


class UnitOfWork:
    """Manage changes for a business transaction.

    Example:

        with UnitOfWork(eq, eq) as unit_of_work:
            repo = unit_of_work.using(EventSourcedRepositoryClass)
            # Put aggreates in or retrieve them from repo
            # Modify aggregates from the repo
        # All changes will be saved and committed at the end
        # of the block or a ConflictError will be raised
        # with the uncommitted events as its payload

    """

    class State(Enum):
        initialized = 0
        begun = 1
        committed = 2
        aborted = 3

    def __init__(self, transient_event_queue, persistent_event_store):
        self._transient_event_queue = transient_event_queue
        self._persistent_event_store = persistent_event_store
        self._event_store_interceptor = _ReadThroughEventStoreWriteInterceptor(self, persistent_event_store)
        self._repos = {}  # repo_factories: repo_instance
        self._state = UnitOfWork.State.initialized
        self._latest_timestamp = None
        self._uncommitted_events = ()

    def __enter__(self):
        return self.begin()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Determine whether to commit() or abort()
        if exc_type is None:
            self.commit()
            return False
        self._uncommitted_events = self.abort()
        return True

    @property
    def uncommitted_events(self):
        return self._uncommitted_events

    def begin(self):
        if self._state != UnitOfWork.State.initialized:
            raise RuntimeError("Cannot begin unit-of-work that is already {!s} and not only {!s}".format(
                self._state, UnitOfWork.State.initialized))

        # 0. Bookmark the current state from the event store.
        self._latest_timestamp = self._begin_timestamp()
        self._state = UnitOfWork.State.begun
        return self

    def _begin_timestamp(self):
        try:
            latest_event = self._persistent_event_store.latest()
        except ValueError:
            return monotonic_utc_now()
        else:
            return latest_event.timestamp

    def commit(self):
        if self._state != UnitOfWork.State.begun:
            raise RuntimeError("Cannot commit a unit-of-work that is {!s} and not {!s}.".format(
                self._state, UnitOfWork.State.begun))

        self._save_all_changes()

        # Check that we're committing onto an expected state - we use timestamps but we could have used versions

        # Determine the identity of all the aggregates that have been modified in this unit-of-work
        modified_aggregate_ids = set(event.aggregate_id for event in self._event_store_interceptor.pending_events())

        # Get the timestamp of the most recent *persisted* event pertaining to each of these aggregates.
        modification_timestamps = {}
        for event in self._persistent_event_store:
            if event.aggregate_id in modified_aggregate_ids:
                modification_timestamps[event.aggregate_id] = max(modification_timestamps.get(event.aggregate_id, 0.0),
                                                                  event.timestamp)

        # Check that none of the modified aggregates have been modified more recently than the beginning
        # of this unit-of work
        for aggregate_id, modification_timestamp in modification_timestamps.items():
            if modification_timestamp > self._latest_timestamp:
                self._uncommitted_events = self.abort()
                raise ConflictError(
                    "Could not commit unit-of-work. The most recent persisted version of aggregate {} at timestamp {} "
                    "is more recent than the expected latest timestamp of {}".format(
                        aggregate_id, modification_timestamp, self._latest_timestamp),
                    events=self._uncommitted_events)

        self._event_store_interceptor.flush()
        self._state = UnitOfWork.State.committed

    def abort(self):
        """Abort a unit-of-work.

        Pending changes will not be committed to the persistent event store.

        Returns:
            The sequence of uncommitted events, which may be inspected for diagnostic purposes or used to 'rebase'
            the operation.

        Raises:
            RuntimeError: If the unit-of-work is not in the expected state.
        """
        if self._state != UnitOfWork.State.begun:
            raise RuntimeError("Cannot abort a unit-of-work that is {!s} and not {!s}.".format(
                self._state, UnitOfWork.State.begun))

        # Saving all changes here in the abort method may seem off, but saving all pending events to the event store
        # interceptor allows us to capture and return all pending events, and also remove
        self._save_all_changes()
        pending_events = tuple(self._event_store_interceptor.pending_events())
        self._event_store_interceptor = None

        self._repos.clear()
        self._state = UnitOfWork.State.aborted
        return pending_events

    def using(self, repository_factory):
        """Create a repository instance for use with this unit-of-work.

        For changes to be under the auspices of the unit-of-work, all repositories must be
        created by passing a repository factory - such as the repository class object - to
        this method.

        Args:
            repository_factory: A two-argument callable that will be passed the
                transient_event_queue and the event store. The
        """
        if self._state != UnitOfWork.State.begun:
            raise RuntimeError("Cannot use a unit-of-work that is {!s} and not {!s}.".format(
                self._state, UnitOfWork.State.begun))
        if repository_factory not in self._repos:
            self._repos[repository_factory] = repository_factory(
                transient_event_queue=self._transient_event_queue,
                persistent_event_store=self._event_store_interceptor
            )
        return self._repos[repository_factory]

    def _save_all_changes(self):
        for repo in self._repos.values():
            repo.save_changes()


class _ReadThroughEventStoreWriteInterceptor(AbstractEventStore):
    """Used as a write-buffer for the underlying event store.

    Instance of this class are used by UnitOfWork to buffer
    writes to the event store so that writes to the event
    store from the pending event stream are under control of
    the unit-of-work.
    """

    def __init__(self, unit_of_work, persistent_event_store):
        self._unit_of_work = unit_of_work
        self._persistent_event_store = persistent_event_store
        self._events = []
        self._require_sort = False

    def append(self, event):
        if self._unit_of_work._state != UnitOfWork.State.begun:
            raise RuntimeError("Cannot use a unit of work that is {!s} rather than {!s}".format(
                self._unit_of_work._state, UnitOfWork.State.begun))
        self._events.append(event)
        self._require_sort = True

    def extend(self, events):
        if self._unit_of_work._state != UnitOfWork.State.begun:
            raise RuntimeError("Cannot use a unit of work that is {!s} rather than {!s}".format(
                self._unit_of_work._state, UnitOfWork.State.begun))
        self._events.extend(events)
        self._require_sort = True

    def flush(self):
        self._ensure_sorted_by_timestamp()
        self._persistent_event_store.extend(self._events)

    def pending_events(self):
        self._ensure_sorted_by_timestamp()
        return iter(self._events)

    def __iter__(self):
        return chain((event for event in self._persistent_event_store
                      if event.timestamp <= self._unit_of_work._latest_timestamp),
                     self.pending_events())

    def _ensure_sorted_by_timestamp(self):
        if self._require_sort:
            self._events.sort(key=lambda event: event.timestamp)
            self._require_sort = False
