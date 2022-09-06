from bot.models import ConfigModel, EnvModel
from bot.extensions import db
import json


def list_config():
    data = ConfigModel.query.all()
    return data


def get_config(owner, repo):
    data = ConfigModel.query.filter_by(owner=owner, repo=repo).first()
    return data


def add_config(owner, repo, config):
    if not isinstance(config, str):
        config = json.dumps(config)
    data = {
        "owner": owner,
        "repo": repo,
        "config": config
    }
    db_data = ConfigModel(**data)
    db.session.add(db_data)
    db.session.commit()
    return db_data


def list_env():
    data = EnvModel.query.all()
    return data


def get_env(owner, repo):
    data = EnvModel.query.filter_by(owner=owner, repo=repo).first()
    return data


def add_env(owner, repo, etag):
    data = {
        "owner": owner,
        "repo": repo,
        "etag": etag
    }
    db_data = EnvModel(**data)
    db.session.add(db_data)
    db.session.commit()
    return db_data


def update_env(owner, repo, etag):
    db_data = EnvModel.query.filter_by(owner=owner, repo=repo).first()
    db_data.etag = etag
    db.session.commit()
    return db_data
