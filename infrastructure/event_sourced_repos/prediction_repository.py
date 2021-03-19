from contexts.prediction.domain.model import prediction
from library.infrastructure_architecture.event_sourced_architecture.event_tracking_repository import \
    EventTrackingRepository


class PredictionRepository(prediction.Repository, EventTrackingRepository):
    """Concrete repository for Transcripts for Event Store
    """

    def __init__(self, transient_event_queue, persistent_event_store, **kwargs):
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

            **kwargs: Arguments to be forwarded to other base classes.
        """
        super().__init__(transient_event_queue=transient_event_queue,
                         persistent_event_store=persistent_event_store,
                         mutator=prediction.mutate,
                         **kwargs)

    def put(self, prediction):
        """Make the repository aware of an aggregate.

        This method is idempotent.

        Args:
            prediction: The aggregate to register with the repository.
        """
        self._register(prediction)

    def prediction_ids(self):
        """An iterable series of prediction IDs."""
        return self._extant_aggregate_ids()

    def prediction_with_id(self, prediction_id):
        """Retrieve a Transcript by ID.

        Args:
            prediction_id: An UniqueId corresponding to the Prediction.

        Returns:
            The Prediction.

        Raises:
            ValueError: If a Prediction with the id could not be found.
        """
        return self._aggregate_with_id(prediction_id)

    def predictions_with_ids(self, prediction_ids=None):
        """Retrieve multiple Predictions by id.

        Args:
            prediction_ids: An optional iterable series of UniqueIds to
                which the results will be restricted. If None, all transcripts
                will be returned.

        Returns:
            An iterable series of Predictions.
        """
        return self._aggregates_with_ids(prediction_ids)

    def predictions_with_phrase(self, phrase, prediction_ids=None):
        """Retrieve Predictions by phrase.

        Args:
            phrase (str): Predictions with phrases equal to this value will
                be included in the result.

            prediction_ids: An optional iterable series of UniqueIds to
                which the results will be restricted. If None, all predictions
                matching phrase will be returned.

        Returns:
            An iterable series of Predictions.
        """
        return filter(lambda prediction: prediction.phrase == phrase,
                      self.predictions_with_ids(prediction_ids))

    def _aggregate_root_entity_class(self):
        return prediction.Prediction
