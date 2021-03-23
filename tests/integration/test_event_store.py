import pytest


from library.infrastructure_architecture.event_sourced_architecture.event_queue import EventQueue
from library.infrastructure_architecture.event_sourced_architecture.event_queue_subscriber import EventQueueSubscriber
from library.infrastructure_architecture.event_sourced_architecture.event_store import EventStore
from library.infrastructure_architecture.event_sourced_architecture.unit_of_work import UnitOfWork, ConflictError
from contexts.prediction.domain.model.prediction import create_prediction
from infrastructure.event_sourced_repos.prediction_repository import PredictionRepository


def test_prediction_in_event_store_saving_and_retrieving_one():
    events = []

    es = EventStore(events)
    eq = EventQueue()
    eqs = EventQueueSubscriber(eq)

    u1 = UnitOfWork(eq, es)
    u1.begin()
    w1 = create_prediction("Foo bar baz", "en-US")
    u1.using(PredictionRepository).put(w1)
    u1.commit()

    u2 = UnitOfWork(eq, es)
    u3 = UnitOfWork(eq, es)

    u2.begin()
    u3.begin()

    w2 = u2.using(PredictionRepository).prediction_with_id(w1.id)
    w3 = u3.using(PredictionRepository).prediction_with_id(w1.id)

    assert w1.id == w2.id == w3.id
    assert (w1 is not w2) and (w2 is not w3)

    eqs.close()
    eq.close()

def test_prediction_in_event_store_saving_and_retrieving_multiple():
    events = []

    es = EventStore(events)
    eq = EventQueue()
    eqs = EventQueueSubscriber(eq)

    for x in range(10):
        u1 = UnitOfWork(eq, es)
        u1.begin()
        w1 = create_prediction("Foo bar baz {index}".format(index=x), "en-US")
        u1.using(PredictionRepository).put(w1)
        u1.commit()

    u2 = UnitOfWork(eq, es)
    u2.begin()
    w2 = u2.using(PredictionRepository).predictions_with_ids()
    
    assert len(list(w2)) == 10

    eqs.close()
    eq.close()


