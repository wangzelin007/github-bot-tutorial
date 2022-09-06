from apiflask import Schema
from sqlalchemy.databases import mysql
from apiflask.fields import Integer, String, Field
from bot.extensions import db


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
    etag = db.Column(db.String(72))


class EnvOutSchema(Schema):
    owner = String()
    repo = String()
    etag = String()
