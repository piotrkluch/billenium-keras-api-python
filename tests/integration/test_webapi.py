from aiohttp import web
from webapi.routes import setup_routes
from webapi.model import init_model, close_model
from config.config import Config

def create_application():
    app = web.Application()
    app['config'] = Config
    app.on_startup.append(init_model)
    app.on_cleanup.append(close_model)
    app = setup_routes(app)
    return app

async def get_client(aiohttp_client, loop):
    return await aiohttp_client(create_application())

async def test_get_api_index(aiohttp_client, loop):
    client = await get_client(aiohttp_client, loop)
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert '200' in text

async def test_predict(aiohttp_client, loop):
    client = await get_client(aiohttp_client, loop)
    request_body = {'data': ['Foo foo foo', 'bar bar bar', 'baz baz baz', 
                             'the brown fox', 'jumped over lazy', 'dog']}
    resp = await client.post('/predict', json=request_body)
    assert resp.status == 200
    text = await resp.text()
    assert 'Foo foo foo' in text
    assert 'the brown fox' in text
    assert 'jumped over lazy' in text
