from webapi.logic import create_application

async def get_client(aiohttp_client):
    return await aiohttp_client(create_application())

async def test_get_api_status(aiohttp_client):
    client = await get_client(aiohttp_client)

    resp = await client.get('/api/v1/')
    assert resp.status == 200

    text = await resp.text()
    assert 'running' in text

async def test_predict(aiohttp_client):
    client = await get_client(aiohttp_client)
    headers = {'X-API-Key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJhZG1pbiJ9.pVAm6V1ybQDZm1Fl0P2ToucSgqNHWJunRpzjSURqF6M'}

    request_body = {'data': ['Foo foo foo', 'bar bar bar', 'baz baz baz', 
                             'the brown fox', 'jumped over the', 'lazy dog']}
    resp = await client.post('/api/v1/predict', json=request_body, headers=headers)
    assert resp.status == 200
    
    text = await resp.text()
    assert 'Foo foo foo' in text
    assert 'the brown fox' in text
    assert 'jumped over the' in text

async def test_predict_no_data_parameter_status_400(aiohttp_client):
    client = await get_client(aiohttp_client)
    headers = {'X-API-Key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJhZG1pbiJ9.pVAm6V1ybQDZm1Fl0P2ToucSgqNHWJunRpzjSURqF6M'}

    request_body = {'foobar': ['Foo foo foo', 'bar bar bar', 'baz baz baz', 
                              'the brown fox', 'jumped over the', 'lazy dog']}
    resp = await client.post('/api/v1/predict', json=request_body, headers=headers)
    assert resp.status == 400
    
    text = await resp.text()
    assert 'Missing parameter: data' in text

async def test_predict_no_model_loaded_status_500(aiohttp_client):
    client = await get_client(aiohttp_client)
    client.app._subapps[0]._state['model'] = None

    headers = {'X-API-Key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJhZG1pbiJ9.pVAm6V1ybQDZm1Fl0P2ToucSgqNHWJunRpzjSURqF6M'}

    request_body = {'data': ['Foo foo foo', 'bar bar bar', 'baz baz baz', 
                              'the brown fox', 'jumped over the', 'lazy dog']}
    resp = await client.post('/api/v1/predict', json=request_body, headers=headers)
    assert resp.status == 500
    
    text = await resp.text()
    assert '500 Internal Server Error' in text

async def test_security_api_key_request(aiohttp_client):
    client = await get_client(aiohttp_client)

    headers_real = {'X-API-Key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJhZG1pbiJ9.pVAm6V1ybQDZm1Fl0P2ToucSgqNHWJunRpzjSURqF6M'}
    request_body = {'data': []}
    resp = await client.post('/api/v1/predict', json=request_body, headers=headers_real)
    assert resp.status == 200

    headers_fake = {'X-API-Key': 'QWERTYIOOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJhZG1pbiJ9.pVAm6V1ybQDZm1Fl0P2ToucSgqNHWJunRpzjSURqF6M'}
    request_body = {'data': []}
    resp = await client.post('/api/v1/predict', json=request_body, headers=headers_fake)
    assert resp.status != 200
