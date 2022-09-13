# -*- coding: utf-8 -*-
import os
from apiflask import APIFlask
from bot.extensions import db, cache, scheduler
from bot.settings import config
from bot.blueprints.github import github_bp
from bot.blueprints.devops import devops_bp


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = APIFlask('bot')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    db.init_app(app)
    cache.init_app(app)
    scheduler.init_app(app)


def register_blueprints(app):
    app.register_blueprint(github_bp)
    app.register_blueprint(devops_bp)
