from aiohttp import web

# =============================================================================
# Main routes import
#
from webapi.views import (
    get_api_index,
    predict
)

# =============================================================================
# Middleware
#

from webapi.middleware import (
   middleware_authenticate
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
def setup_routes(subapp):
    subapp.router.add_route('GET',  '/',        get_api_index)
    subapp.router.add_route('POST', '/predict', middleware_authenticate, predict)
    return subapp
