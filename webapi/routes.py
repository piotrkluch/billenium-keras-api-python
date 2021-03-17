from aiohttp import web

# =============================================================================
# Main routes import
#
from webapi.views import (
    get_api_index
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
    app.router.add_route('GET', '/', get_api_index)
    return app
