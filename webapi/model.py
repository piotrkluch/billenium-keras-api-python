import os
import tensorflow as tf
from config.paths import Paths

from library.infrastructure_architecture.event_sourced_architecture.event_queue import EventQueue
from library.infrastructure_architecture.event_sourced_architecture.event_queue_subscriber import EventQueueSubscriber
from library.infrastructure_architecture.event_sourced_architecture.event_store import JsonFileStore, EventStore
from library.infrastructure_architecture.event_sourced_architecture.transcoders import ObjectJSONEncoder, \
    ObjectJSONDecoder


def load_keras_model(app):
    conf = app['config']
    model_path = os.path.join(conf['root_dir'], 'resources/models/', conf['keras_model_name'])
    model = tf.keras.models.load_model(model_path)
    app['model'] = model

async def init_model(app):
    load_keras_model(app)
    init_event_store(app)

def init_event_store(app):
    conf = app['config']
    jfs = JsonFileStore(store_path=os.path.join(Paths.directories['database_dir'], 'store.events'),
                        json_encoder_class=ObjectJSONEncoder,
                        json_decoder_class=ObjectJSONDecoder)
    es = EventStore(jfs)
    eq = EventQueue()
    eqs = EventQueueSubscriber(eq)
    app['jfs'] = jfs
    app['es'] = es
    app['eq'] = eq
    app['eqs'] = eqs

async def close_model(app):
    app['eqs'].close()
    app['eq'].close()
