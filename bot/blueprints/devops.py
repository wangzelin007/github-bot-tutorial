from apiflask import APIFlask, HTTPBasicAuth, APIBlueprint
from bot.utils.request_client import RequestHandler
import logging
from flask import request


devops_bp = APIBlueprint('devops', __name__)
app = APIFlask('bot')
auth = HTTPBasicAuth()
requestClient = RequestHandler()
logger = logging.getLogger('bot')


# Azure DevOps webhook with username:password
@devops_bp.route('/devops', methods=['POST'])
@devops_bp.auth_required(auth)
def webhook2():
    event = request.json
    print(event)
    app.logger.info("====== event: %s ======", event)
    return 'Hello azclitools!'