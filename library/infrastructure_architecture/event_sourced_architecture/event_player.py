from collections import defaultdict
from functools import reduce


def replay_events(*, events, mutator, aggregate_ids, stream_primer=None):
    """Lazily replay all events or the supplied aggregate_ids.

    To force evaluation the iterator must be consumed.

    Args:
        events: An iterable series of events from which an iterator can be obtained.

        mutator: A function of two arguments which is used to apply changes represented by
            events to the state (e.g. entity) . The function must accept the current state
            as its left argument, and event which will cause the state to be modified as its
            right argument. The function must return a new state, which may or may not be the
            same object as the state argument.

        aggregate_ids: A container of aggregate IDs for which events will be replayed.

        stream_primer: An optional initial value for the state, otherwise None.

        Returns:
            An iterable series of entities reconstituted from the event stream.
    """
    ep = EventPlayer(events, mutator, stream_primer)
    return ep.replay_events(aggregate_ids)


class EventPlayer:
    """Replaying events.
    """

    def __init__(self, events, mutator, stream_primer):
        """Create a new EventPlayer.

        Args:
            events: An iterable series of events from which an iterator can be obtained.

            mutator: A function of two arguments which is used to apply changes represented by
                events to the state (e.g. entity) . The function must accept the current state
                as its left argument, and event which will cause the state to be modified as its
                right argument. The function must return a new state, which may or may not be the
                same object as the state argument.

            stream_primer: The initial value for the state.
        """
        self._events = events
        self._mutator = mutator
        self._stream_primer = stream_primer

    def replay_events(self, aggregate_ids):
        """Lazily replay all events for the supplied aggregate_ids.

        Args:
            aggregate_ids: A container of aggregate IDs for which events will be replayed.

        Returns:
            An iterable series of aggregate root entities reconstituted from the event stream.
        """
        aggregate_to_events = self._group_events_by_aggregate_id(aggregate_ids)
        all_entities = map(self._reconstitute, aggregate_to_events.values())
        return all_entities

    def _group_events_by_aggregate_id(self, aggregate_ids):
        """Group events for the given aggregate IDs by aggregate ID.

        Args:
            aggregate_ids: A container of aggregate IDs.

        Returns:
            A dictionary where each item maps an aggregate id to an ordered list
            of events pertaining to that aggregate.
        """
        aggregate_to_events = defaultdict(list)
        for event in self._events:
            if event.aggregate_id in aggregate_ids:
                aggregate_to_events[event.aggregate_id].append(event)
        return aggregate_to_events

    def _reconstitute(self, events):
        """Reconstitute an object from a series of events.

        Args:
            stored_events: A container of stored events. All events in the
                supplied stream must pertain to the same aggregate.

        Returns:
            The object obtained by applying the stored events.
        """
        # Current state is the left fold over previous behaviours - Greg Young
        return reduce(self._mutator, events, self._stream_primer)
