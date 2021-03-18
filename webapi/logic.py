########################################
# Init for local development and testing
#
import asyncio
import os
from aiohttp import web

from config.config import Config
from webapi.routes import setup_routes

import tensorflow as tf


def load_model():
    model_path = os.path.join(Config['root_dir'], 'resources/models/', Config['keras_model_name'])
    model = tf.keras.models.load_model(model_path)
    print(model.summary())
    print(model.predict(["Hello"]))

def main():
    load_model()
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app = setup_routes(app)
    web.run_app(app,
                host=Config['webapi_host'],
                port=Config['webapi_port'])
    return app

#TODO: Add CORS support (security)
#TODO: Add middleware layer (security)
