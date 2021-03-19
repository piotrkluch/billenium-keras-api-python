import warnings
from collections import deque


class EventQueue:
    """An in-memory series of events.
    """

    def __init__(self, events=None):
        if events is None:
            events = deque()
        self._events = deque(events)
        self._closed = False

    def append(self, event):
        """Append an event to the queue.

        Args:
            event: The event to be appended.

        Raises:
            RuntimeError: If close() has been previously called.
        """
        if self._closed:
            raise RuntimeError("Cannot append. {!r} has been closed.".format(self))
        self._events.append(event)

    def __len__(self):
        """The number of events in the queue."""
        return len(self._events)

    def __iter__(self):
        """Obtain an iterator over the events in the queue."""
        yield from self._events

    def separate_out(self, predicate):
        """Separate out all the events matching the predicate.

        This function returns all events which match the predicate,
        removing them from the queue.

        Args:
            predicate: A single-argument function used to
                partition the events into two series. Events
                for which the predicate returns False are
                retained in order. Events for which the
                predicate returns True are returned, in order.

        Returns:
            A deque of events which match the predicate.
        """
        non_matching = deque()
        matching = deque()

        while len(self._events) != 0:
            event = self._events.popleft()
            if predicate(event):
                matching.append(event)
            else:
                non_matching.append(event)

        self._events = non_matching
        return matching

    def close(self):
        """Close the queue.

        Once closed, any further calls to append will raise a RuntimeError.

        If the queue is not empty when closed, a warning will be printed to the console.
        """
        self._closed = True
        if len(self) != 0:
            warnings.warn("{!r} contains {} unretrieved events on close".format(self, len(self)),
                          RuntimeWarning)

    def clear(self):
        """Discard all events in the queue."""
        self._events.clear()