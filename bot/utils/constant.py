import os
import logging


logger = logging.getLogger('bot')


GH_SECRET = os.environ.get("GH_SECRET")
GH_AUTH = os.environ.get("GH_AUTH")
HEADERS = {
    'Accept': 'application/vnd.github+json',
    'Authorization': 'token %s' % GH_AUTH
}
logger.info("====== HEADERS: %s ======", HEADERS)
CONFIG_BASE_URL='https://raw.github.com'
CONFIG_URL_POSTFIX='HEAD/.github/azure-cli-bot-dev.json'
