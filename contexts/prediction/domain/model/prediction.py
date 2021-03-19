from abc import ABCMeta, abstractmethod
from functools import singledispatch

from config.config import Config
from library.domain.entity import Entity
from library.domain.events import DomainEvent, publish


# ======================================================================================================================
# Aggregate root entity
#
from library.domain.exceptions import ConstraintError
from utilities.unique_id import make_unique_id


class Prediction(Entity):
    class Created(Entity.Created):
        pass

    class Discarded(Entity.Discarded):
        pass

    def __init__(self, event):
        """Initialize new prediction

        Do not call directly, use the factory method."""
        super().__init__(event.entity_id, event.entity_version, )

        self._phrase = event.phrase
        self._language = event.language
        self._output = event.output

    def __repr__(self):
        return "{discarded}Prediction(" \
               "id={prediction._id}, " \
               "name={prediction._name})" \
            .format(discarded="*Discarded* " if self._discarded else "", prediction=self)

    # [phrase]
    @property
    def phrase(self):
        """Name this prediction"""
        self._check_not_discarded()
        return self._phrase
    #[/phrase]

    # [language]
    @property
    def language(self):
        """Name this prediction"""
        self._check_not_discarded()
        return self._language
    #[/language]

    def _apply(self, event):
        mutate(self, event)
        pass



# ======================================================================================================================
# Entities
#


# ======================================================================================================================
# Factories - the aggregate root factory
#

def create_prediction(name):
    prediction_id = make_unique_id()

    event = Prediction.Created(aggregate_id=prediction_id,
                               entity_id=prediction_id,
                               entity_version=0,
                               phrase=Prediction._validate_name(name))

    prediction = _when(event)
    event._aggregate_instance_id = prediction.instance_id
    publish(event)
    return prediction

# ======================================================================================================================
# Mutators - all aggregate creation and mutation is performed by the generic _when() function.
#

def mutate(obj, event):
    return _when(event, obj)


# These dispatch on the type of the first arg, hence (event, self)
@singledispatch
def _when(event, entity):
    """Modify an entity (usually an aggregate root) by replaying an event."""
    raise NotImplementedError("No _when() implementation for {!r} against {!r}".format(event, entity))

@_when.register(Prediction.Created)
def _(event, unused=None):
    """Create a new aggregate root"""
    assert unused is None
    prediction = Prediction(event)
    return prediction

@_when.register(Prediction.Discarded)
def _(event, prediction):
    prediction._validate_event_applicability(event)
    prediction._discarded = True
    prediction._increment_version()
    return prediction



# ======================================================================================================================
# Repository - for retrieving existing aggregates
#

class Repository(metaclass=ABCMeta):

    @abstractmethod
    def put(self, prediction):
        raise NotImplementedError

    @abstractmethod
    def prediction_with_id(self, prediction_id):
        raise NotImplementedError

    @abstractmethod
    def predictions_with_ids(self, prediction_ids=None):
        raise NotImplementedError

    @abstractmethod
    def predictions_with_name(self, name, prediction_ids=None):
        raise NotImplementedError




# ======================================================================================================================
# Exceptions - for signalling errors
#

class LimitError(ConstraintError):
    pass