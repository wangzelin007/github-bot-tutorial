from bot.extensions import db
from apiflask import APIFlask, Schema
from sqlalchemy.databases import mysql
import os
from apiflask.fields import Integer, String, Field
import json


class ConfigModel(db.Model):
    owner = db.Column(db.String(36), primary_key=True)
    repo = db.Column(db.String(36), primary_key=True)
    config = db.Column(mysql.MSMediumText, nullable=False)


class ConfigOutSchema(Schema):
    owner = String()
    repo = String()
    config = String()


class EnvModel(db.Model):
    owner = db.Column(db.String(36), primary_key=True)
    repo = db.Column(db.String(36), primary_key=True)
    etag = db.Column(db.String(36))
    config_url = db.Column(db.String(128))
    base_url = db.Column(db.String(36))
    issue_url = db.Column(db.String(36))
    pr_url = db.Column(db.String(36))


class EnvOutSchema(Schema):
    owner = String()
    repo = String()
    etag = String()
    config_url = String()
    base_url = String()
    issue_url = String()
    pr_url = String()
