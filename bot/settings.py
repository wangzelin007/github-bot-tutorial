# -*- coding: utf-8 -*-
import os


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
USERNAME = os.getenv('BOT_DB_USER', 'secret string')
PASSWORD = os.getenv('BOT_DB_PASS', 'secret string')


class BaseConfig(object):
    SCHEDULER_API_ENABLED = True

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    BASE_RESPONSE_SCHEMA = None

    CACHE_TYPE = 'FileSystemCache'
    CACHE_ARGS = []
    CACHE_OPTIONS = {}
    CACHE_DEFAULT_TIMEOUT = 36000
    CACHE_IGNORE_ERRORS = True
    CACHE_THRESHOLD = 100
    CACHE_DIR = 'cache'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@azure-cli-bot-db-dev.mysql.database.azure.com/azure_cli_bot_dev?ssl_ca=DigiCertGlobalRootCA.crt.pem'


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@azure-cli-bot-db-dev.mysql.database.azure.com/azure_cli_bot_dev?ssl_ca=DigiCertGlobalRootCA.crt.pem'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
