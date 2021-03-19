import os
import tensorflow as tf


def load_keras_model(app):
    conf = app['config']
    model_path = os.path.join(conf['root_dir'], 'resources/models/', conf['keras_model_name'])
    model = tf.keras.models.load_model(model_path)
    app['model'] = model

async def init_model(app):
    load_keras_model(app)
    init_event_store(app)

def init_event_store(app):
    pass

async def close_model(app):
    pass
