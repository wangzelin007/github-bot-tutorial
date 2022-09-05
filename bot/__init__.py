# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import Flask, request
from bot.extensions import db  # , bootstrap, migrate
from bot.settings import config
from bot.blueprints.github import github_bp

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# logger = logging.getLogger(__name__)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bot')
    app.config.from_object(config[config_name])

    register_logging(app)
    app.logger.debug('no log????')
    app.logger.info('no log????')
    app.logger.warning('no log????')
    register_extensions(app)
    register_blueprints(app)
    return app


def register_logging(app):
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s-%(filename)s-%(levelname)s: %(message)s')

    file_handler = RotatingFileHandler(
        os.path.join(basedir, os.getenv('LOG_FILE', 'logs/bot-debug.log')),
        maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    request_handler = RotatingFileHandler(
        os.path.join(basedir, os.getenv('LOG_FILE', 'logs/bot-error.log')),
        maxBytes=10 * 1024 * 1024, backupCount=10)
    request_handler.setLevel(logging.ERROR)
    request_handler.setFormatter(request_formatter)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(request_handler)



def register_extensions(app):
    # bootstrap.init_app(app)
    db.init_app(app)
    # migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(github_bp)