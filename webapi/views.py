from aiohttp import web


async def get_api_index(request):
    body = {'status_code': 200}
    return web.json_response(body)
