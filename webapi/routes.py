from aiohttp import web

# =============================================================================
# Main routes import
#
from webapi.views import (
    get_api_index,
    predict
)

# =============================================================================
# Routes go here
#
#  ▪▄▄▄▄         ▄• ▄▌▄▄▄▄▄▄▄▄ ..▄▄ · 
#    ▀▄ █·▪     █▪██▌•██  ▀▄.▀·▐█ ▀. 
#    ▐▀▀▄  ▄█▀▄ █▌▐█▌ ▐█.▪▐▀▀▪▄▄▀▀▀█▄
#    ▐█•█▌▐█▌.▐▌▐█▄█▌ ▐█▌·▐█▄▄▌▐█▄▪▐█
#    .▀  ▀ ▀█▄▀▪ ▀▀▀  ▀▀▀  ▀▀▀  ▀▀▀▀ 
#
#
def setup_routes(app):
    app.router.add_route('GET',  '/',        get_api_index)
    app.router.add_route('POST', '/predict', predict)
    return app
