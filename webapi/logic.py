########################################
# Init for local development and testing
#
import asyncio
from aiohttp import web

from config.config import Config
from webapi.routes import setup_routes

def main():
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app = setup_routes(app)
    web.run_app(app,
                host=Config['webapi_host'],
                port=Config['webapi_port'])
    return app

#TODO: Add CORS support (security)
#TODO: Add middleware layer (security)
