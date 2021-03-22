##########################################################
# Init logic for local development, testing and production
#
import asyncio
from aiohttp import web
from aiohttp_route_middleware import UrlDispatcherEx
import aiohttp_cors

from config.config import Config
from webapi.routes import setup_routes
from webapi.model import init_model, close_model


def create_application():
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    subapp = web.Application(router=UrlDispatcherEx())
    subapp = setup_routes(subapp)
    subapp['config'] = Config
    subapp.on_startup.append(init_model)
    subapp.on_cleanup.append(close_model)
    app.add_subapp('/api/v1', subapp)
    return app

def setup_cors(app):
    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })

    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)
    return app

def main():
    app = create_application()
    app = setup_cors(app)
    web.run_app(app,
                host=Config['webapi_host'],
                port=Config['webapi_port'])
    return app