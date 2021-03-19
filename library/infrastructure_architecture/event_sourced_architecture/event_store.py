import json

from library.infrastructure_architecture.event_sourced_architecture.abstract_event_store import AbstractEventStore
from utilities.identifiers import class_to_qualname, qualname_to_class
from utilities.itertools import last


class JsonFileStore:

    def __init__(self, store_path, json_encoder_class=None, json_decoder_class=None):
        """Open an event store.

        Args:
            store_path: The path to a new or existing event store.
            json_decoder_class: An optional custom JSONEncoder subclass.
        """
        self._store_path = store_path
        self._json_encoder_class = json_encoder_class
        self._json_decoder_class = json_decoder_class
        open(self._store_path, 'a').close()

    def append(self, obj):
        with open(self._store_path, 'a+t') as store_file:
            json.dump(obj, store_file, separators=(',',':'), sort_keys=True, cls=self._json_encoder_class)
            store_file.write('\n')

    def extend(self, objs):
        with open(self._store_path, 'a+t') as store_file:
            for obj in objs:
                json.dump(obj, store_file, separators=(',',':'), sort_keys=True, cls=self._json_encoder_class)
                store_file.write('\n')

    def __iter__(self):
        with open(self._store_path, 'rt') as store_file:
            for line in store_file:
                obj = json.loads(line, cls=self._json_decoder_class)
                yield obj

    def latest(self):
        return last(self)


class EventStore(AbstractEventStore):

    def __init__(self, store, publisher=None):
        self._store = store
        self._publisher = publisher if publisher is not None else lambda e: None

    def extend(self, events):
        """Store a series of events.

        Args:
            events: An iterable collection of events.
        """
        self._store.extend(self._event_to_dict(event) for event in events)
        for event in events:
            self._publisher(event)

    def __iter__(self):
        for obj in self._store:
            event = self._dict_to_event(obj)
            yield event

    def _event_to_dict(self, event):
        topic = class_to_qualname(type(event))
        attributes = {key: value for key, value in vars(event).items() if not key.startswith('_')}
        obj = dict(__event_type=type(event).__qualname__, topic=topic, attributes=attributes)
        return obj

    def _dict_to_event(self, obj):
        topic = obj['topic']
        cls = qualname_to_class(topic)
        attributes = obj['attributes']
        event = cls(**attributes)
        return event
