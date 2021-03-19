########################################
# Init for local development and testing
#
import asyncio
import os
from aiohttp import web

from config.config import Config
from webapi.routes import setup_routes
from webapi.model import init_model, close_model


def main():
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    
    app['config'] = Config
    app.on_startup.append(init_model)
    app.on_cleanup.append(close_model)

    app = setup_routes(app)
    web.run_app(app,
                host=Config['webapi_host'],
                port=Config['webapi_port'])
    return app

#TODO: Add CORS support (security)
#TODO: Add middleware layer (security)
