from aiohttp import web
from config.config import Config
import jwt


@web.middleware
async def middleware_authenticate(request, handler):
    key = request.headers.get('X-API-Key')

    try:
        decoded = jwt.decode(key, Config['keras_api_key_secret'], verify=True, algorithms=["HS256"])
    except Exception as err:
        print("OS error: {0}".format(err))
        return web.json_response(status=400, text="Key invalid")

    response = await handler(request)
    return response