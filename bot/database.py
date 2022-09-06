from bot.models import ConfigModel, EnvModel
from bot.extensions import db


def list_config():
    data = ConfigModel.query.all()
    return data


def get_config(owner, repo):
    data = ConfigModel.query.filter_by(owner=owner, repo=repo).first()
    return data


def add_config(owner, repo, config):
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


def add_env(owner, repo, etag, config_url, base_url, issue_url, pr_url):
    data = {
        "owner": "wangzelin007",
        "repo": "github-bot-tutorial",
        "etag": "etag",
        "config_url": "g.config_url",
        "base_url": "g.config_url",
        "issue_url": "g.config_url",
        "pr_url": "g.config_url"
    }
    db_data = EnvModel(**data)
    db.session.add(db_data)
    db.session.commit()
    return db_data