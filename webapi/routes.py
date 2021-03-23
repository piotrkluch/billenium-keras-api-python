from aiohttp import web

# =============================================================================
# Main routes import
#
from webapi.views import (
    get_api_status,
    predict,
    get_predictions
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
    subapp.router.add_route('GET',  '/',        get_api_status)
    subapp.router.add_route('POST', '/predict', middleware_authenticate, predict)
    subapp.router.add_route('GET', '/predictions', middleware_authenticate, get_predictions)
    return subapp
