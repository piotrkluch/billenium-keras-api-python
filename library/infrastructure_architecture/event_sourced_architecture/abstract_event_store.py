from abc import ABCMeta, abstractmethod

from utilities.containers import universal_container
from utilities.itertools import last
from utilities.time import _MAX_TIMESTAMP

class AbstractEventStore(metaclass=ABCMeta):

    def append(self, event):
        self.extend((event,))

    @abstractmethod
    def extend(self, events):
        raise NotImplementedError

    def events(self, for_aggregate_ids=None, upto_timestamp=None):
        if for_aggregate_ids is None:
            for_aggregate_ids = universal_container()
        if upto_timestamp is None:
            upto_timestamp = _MAX_TIMESTAMP
        for event in self:
            if (event.aggregate_id in for_aggregate_ids) and (event.timestamp < upto_timestamp):
                yield event

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    def latest(self, for_aggregate_ids=None, upto_timestamp=None):
        return last(self.events(for_aggregate_ids, upto_timestamp))