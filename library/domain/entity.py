from abc import ABCMeta, abstractmethod
from itertools import count




# ======================================================================================================================
# Entities
#
from library.domain.events import DomainEvent
from library.domain.exceptions import ConsistencyError


class Entity(metaclass=ABCMeta):
    """The base class of all entities.

    Attributes:
        id: A unique identifier.
        instance_id: A value unique among instances of this entity.
        version: An integer version.
        discarded: True if this entity should no longer be used, otherwise False.
    """

    class Created(DomainEvent):
        pass

    class Discarded(DomainEvent):
        pass

    _instance_id_generator = count()

    @abstractmethod
    def __init__(self, entity_id, entity_version):
        self._id = entity_id
        self._version = entity_version
        self._discarded = False
        self._instance_id = next(Entity._instance_id_generator)

    def _increment_version(self):
        self._version += 1

    @property
    def instance_id(self):
        """A value unique among instances of this entity."""
        return self._instance_id

    @property
    def id(self):
        """A string unique identifier for the entity."""
        return self._id

    @property
    def version(self):
        """An integer version for the entity."""
        return self._version

    def _validate_event_applicability(self, event):
        if event.entity_id != self.id:
            raise ConsistencyError("Event entity id mismatch: {} != {}".format(event.entity_id, self.id))
        if event.entity_version != self.version:
            raise ConsistencyError("Event entity version mismatch: {} != {}".format(event.entity_version,
                                                                                    self.version))

    @property
    def discarded(self):
        """True if this entity is marked as discarded, otherwise False."""
        return self._discarded

    def _check_not_discarded(self):
        if self._discarded:
            raise DiscardedEntityError("Attempt to use {}".format(repr(self)))


# ======================================================================================================================
# Exceptions - for signalling errors
#

class DiscardedEntityError(Exception):
    """Raised when an attempt is made to use a discarded Entity."""
    pass
