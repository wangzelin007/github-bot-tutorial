import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


basedir = os.path.abspath((os.path.dirname(__file__)))
log_file = os.path.join(basedir, os.getenv('LOG_FILE', 'logs/bot.log'))
logging.basicConfig(
    filename=log_file,
    format='[%(asctime)s-%(filename)s-%(levelname)s: %(message)s]',
    level = logging.DEBUG,
    filemode='a',
    datefmt='%Y-%m-%d %I:%M:%S %p')
logger = logging.getLogger('bot')
logger.setLevel(logging.DEBUG)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024, backupCount=10)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-%(filename)s-%(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


from bot import create_app  # noqa


app = create_app('production')
app.run(debug=True)
# app.run()