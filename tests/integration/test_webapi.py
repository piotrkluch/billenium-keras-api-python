from aiohttp import web
from webapi.routes import setup_routes

def create_application():
    app = web.Application()
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
    request_body = {'data': 'data'}
    resp = await client.post('/predict', data=request_body)
    assert resp.status == 200
