##########################################################
# Init logic for local development, testing and production
#
import asyncio
import os
from aiohttp import web
from aiohttp_route_middleware import UrlDispatcherEx
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings
import aiohttp_cors

from config.config import Config
from config.paths import Paths
from webapi.routes import *
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

def setup_swagger(app):
    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path="/docs/"),
        title="API Specification: keras-api-python",
        version="1.0.0",
        components= os.path.join(Paths.directories['webapi_dir'], "components.yaml")
    )
    swagger.add_routes( #TODO: Automagically add all routes
        [
            web.get("/api/v1/", get_api_status),
            web.post("/api/v1/predict", predict),
            web.get("/api/v1/predictions", get_predictions)
        ]
    )
    return app

def main():
    app = create_application()
    app = setup_cors(app)
    app = setup_swagger(app)
    web.run_app(app,
                host=Config['webapi_host'],
                port=Config['webapi_port'])
    return app