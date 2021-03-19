from abc import abstractmethod, ABCMeta
from collections import defaultdict
from itertools import chain
from weakref import WeakValueDictionary

from library.infrastructure_architecture.event_sourced_architecture.event_player import replay_events
from utilities.itertools import deferred_chain, exactly_one


class EventTrackingRepository(metaclass=ABCMeta):
    """An abstract base class for event-store based repositories.
    """

    def __init__(self, transient_event_queue, persistent_event_store, mutator, **kwargs):
        """Initialize.

        It is assumed that the concatenation of the event streams in persistent_event_store
        and transient_event_queue contain all events in which this repository has an interest.

        Args:
            transient_event_queue: An EventQueue from which unsaved and future events
                pertaining to aggregates which will be, or have been, put into this
                repository, can be retrieved. Essentially this is the collection from
                where "present" (happened, but unsaved) and future (yet to happen)
                events can be retrieved.

            persistent_event_store: An EventStore containing past events.

            mutator: A two-argument reducing function which accepts an aggregate as its first
                argument and an event to be applied to the aggregate as its second argument.

            **kwargs: Arguments to be forwarded to other base classes.
        """
        super().__init__(**kwargs)
        self._transient_event_queue = transient_event_queue
        self._persistent_event_store = persistent_event_store
        self._mutator = mutator
        self._tracking_aggregate_ids = defaultdict(set)  # {aggregate.id: {aggregate.instance_id, ...}}
        self._identity_map = WeakValueDictionary()

    @property
    def transient_event_queue(self):
        return self._transient_event_queue

    @property
    def persistent_event_store(self):
        return self._persistent_event_store

    def _intern(self, aggregate_root_entity):
        self._identity_map[aggregate_root_entity.id] = aggregate_root_entity

    def _unintern(self, aggregate_root_entity):
        del self._identity_map[aggregate_root_entity.id]

    def _track(self, aggregate_root_entity):
        self._tracking_aggregate_ids[aggregate_root_entity.id].add(aggregate_root_entity.instance_id)

    def _register(self, aggregate_root_entity):
        """Register an aggregate with this repository.

        Once an aggregate is registered with the repository, the aggregate
        is retrievable from the repository via _aggregate_with_id(), _aggregates_with_ids(),
        and _extant_aggregate_ids()
        """
        if not isinstance(aggregate_root_entity, self._aggregate_root_entity_class()):
            raise TypeError("{!r} is not of type {} therefore cannot be store in a {}"
                            .format(aggregate_root_entity, self._aggregate_root_entity_class().__name__, self.__class__.__name__))
        self._track(aggregate_root_entity)
        self._intern(aggregate_root_entity)

    def _register_iter(self, iterable):
        """Lazily register aggregate root entities as they are yielded by the iterable."""
        for aggregate_root_entity in iterable:
            self._track(aggregate_root_entity)
            self._intern(aggregate_root_entity)
            yield aggregate_root_entity

    def _unregister(self, aggregate_root_entity):
        self._unintern(aggregate_root_entity)

    def is_from_tracked_aggregate(self, event):
        return (event.aggregate_id in self._tracking_aggregate_ids
                and event._aggregate_instance_id in self._tracking_aggregate_ids[event.aggregate_id])

    def save_changes(self):
        """Save all pending changes from tracked aggregates into the persistent event-store."""
        change_events = self._transient_event_queue.separate_out(self.is_from_tracked_aggregate)
        for event in change_events:
            self._persistent_event_store.append(event)

    def __len__(self):
        return len(self._extant_aggregate_ids())

    def _aggregate_with_id(self, entity_id):
        """Obtain an aggregate by aggregate root entity ID.
        """
        try:
            entity = self._instance(entity_id)
        except ValueError:
            entity = self._load_aggregate_with_id(entity_id)
        self._register(entity)
        return entity

    def _aggregates_with_ids(self, entity_ids=None):
        """Obtain a series of aggregates by root entity id.

        Args:
            entity_ids: An iterable series of aggregate root IDs.
        """
        entity_ids = tuple(entity_ids) if entity_ids is not None else entity_ids
        return self._register_iter(
            deferred_chain(lambda: self._instantiated_aggregates(entity_ids),
                           lambda: self._persisted_aggregates(entity_ids)))

    def _instantiated_ids(self):
        """Obtain an iterable series of entity ids."""
        return self._identity_map.keys()

    def _instance(self, aggregate_root_entity_id):
        try:
            return self._identity_map[aggregate_root_entity_id]
        except KeyError:
            raise ValueError("No {} instance with id {}".format(self.__class__.__name__, aggregate_root_entity_id))

    def _instantiated_aggregates(self, aggregate_ids=None):
        """An iterable series of instantiated (in-memory) aggregates."""
        instantiated_work_item_ids = (self._instantiated_ids()
                              if aggregate_ids is None
                              else set(self._instantiated_ids()).intersection(aggregate_ids))
        return map(self._instance, instantiated_work_item_ids)

    def _persisted_aggregates(self, aggregate_ids=None):
        """An iterable series of persisted (not in-memory) aggregates."""
        aggregate_ids = set(aggregate_ids) if aggregate_ids is not None else self._extant_aggregate_ids()
        persisted_entity_ids = aggregate_ids.difference(self._instantiated_ids())
        return self._load_aggregates_with_ids(persisted_entity_ids)

    def _load_aggregate_with_id(self, aggregate_id):
        try:
            return exactly_one(self._load_aggregates_with_ids({aggregate_id}))
        except ValueError as e:
            raise ValueError("No {} with id {}".format(self._aggregate_root_entity_class().__name__, aggregate_id)) from e

    def _load_aggregates_with_ids(self, aggregate_ids):
        assert aggregate_ids.isdisjoint(self._instantiated_ids()), \
               "Cannot load: {} with ids {} which are already instantiated".format(
                    self._aggregate_root_entity_class().__name__, aggregate_ids.intersection(self._instantiated_ids()))
        events = chain(
            self._persistent_event_store,
            filter(self.is_from_tracked_aggregate, self._transient_event_queue))
        aggregate_root_entities = replay_events(events=events, mutator=self._mutator, aggregate_ids=aggregate_ids)
        return aggregate_root_entities

    def _extant_aggregate_ids(self):
        """A set of IDs for aggregates managed by this repository which have not been discarded."""
        events = chain(
            self._persistent_event_store,
            filter(self.is_from_tracked_aggregate, self._transient_event_queue))
        return extant_persisted_aggregate_ids(events, self._aggregate_root_entity_class)

    @abstractmethod
    def _aggregate_root_entity_class(self):
        raise NotImplementedError


# TODO: Refactor this to be a projection
def extant_persisted_aggregate_ids(events, entity_class):
    """Scan all events in an event store to find extant aggregates of a specified type.

    Use this function to find those aggregates which have been created, but not yet
    discarded by the end of the event stream. Such entities are still 'extant'.

    Args:
        events: The event store to search.

        entity_class: The name of an aggregate root entity class (as as string) within
            which <EntityName>.Created and <EntityName>.Discarded event can be
            found.

    Return:
        A set of extant aggregate root entity ids.
    """
    created_event_class = getattr(entity_class(), 'Created', None)
    discarded_event_class = getattr(entity_class(), 'Discarded', None)

    aggregate_ids = set()
    for event in events:
        if isinstance(event, created_event_class):
            aggregate_id = event.aggregate_id
            if aggregate_id in aggregate_ids:
                raise InconsistentEventStreamError("Inconsistent event stream: Duplicate {} creation "
                                                   "for id {}".format(entity_class.__name__, aggregate_id))
            aggregate_ids.add(aggregate_id)

        elif isinstance(event, discarded_event_class):
            aggregate_id = event.aggregate_id
            if aggregate_id not in aggregate_ids:
                raise InconsistentEventStreamError("Inconsistent event stream: Discarding non-existent {} "
                                                   "for id {}".format(entity_class.__name__, aggregate_id))
            aggregate_ids.discard(aggregate_id)
    return aggregate_ids


class InconsistentEventStreamError(Exception):
    pass

