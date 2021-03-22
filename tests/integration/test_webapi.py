import asyncio
from aiohttp import web
from aiohttp_route_middleware import UrlDispatcherEx

from webapi.routes import setup_routes
from webapi.model import init_model, close_model
from config.config import Config

def create_application():
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app['config'] = Config
    app.on_startup.append(init_model)
    app.on_cleanup.append(close_model)
    subapp = web.Application(router=UrlDispatcherEx())
    subapp = setup_routes(subapp)
    app.add_subapp('/api/v1', subapp)
    return app

async def get_client(aiohttp_client, loop):
    return await aiohttp_client(create_application())

async def test_get_api_index(aiohttp_client, loop):
    client = await get_client(aiohttp_client, loop)

    resp = await client.get('/api/v1/')
    assert resp.status == 200

    text = await resp.text()
    assert '200' in text

async def test_predict(aiohttp_client, loop):
    client = await get_client(aiohttp_client, loop)
    headers = {'X-API-Key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJhZG1pbiJ9.pVAm6V1ybQDZm1Fl0P2ToucSgqNHWJunRpzjSURqF6M'}

    request_body = {'data': ['Foo foo foo', 'bar bar bar', 'baz baz baz', 
                             'the brown fox', 'jumped over lazy', 'dog']}
    resp = await client.post('/api/v1/predict', json=request_body, headers=headers)
    assert resp.status == 200
    
    text = await resp.text()
    assert 'Foo foo foo' in text
    assert 'the brown fox' in text
    assert 'jumped over lazy' in text
