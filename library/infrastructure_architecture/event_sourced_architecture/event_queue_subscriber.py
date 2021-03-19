

# TODO: Turn this into a more general class which can subscribe and unsubscribe from
# TODO: anything, with a context manager interface.
from library.domain.events import subscribe, unsubscribe, DomainEvent


class EventQueueSubscriber:

    def __init__(self, event_queue):
        self._event_queue = event_queue
        subscribe(EventQueueSubscriber._all_events, self.enqueue_event)

    def enqueue_event(self, event):
        self._event_queue.append(event)

    @staticmethod
    def _all_events(event):
        return isinstance(event, DomainEvent)

    def close(self):
        unsubscribe(self._all_events, self.enqueue_event)
