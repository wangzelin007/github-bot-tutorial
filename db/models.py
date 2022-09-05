from flask_sqlalchemy import SQLAlchemy
from apiflask import APIFlask, Schema
from sqlalchemy.databases import mysql
import os
from apiflask.fields import Integer, String
import json

USERNAME = os.getenv('BOT_DB_USER', 'secret string')
PASSWORD = os.getenv('BOT_DB_PASS', 'secret string')


app = APIFlask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@azure-cli-bot-db-dev.mysql.database.azure.com/azure_cli_bot_dev?ssl_ca=DigiCertGlobalRootCA.crt.pem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class ConfigModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(36))
    etag = db.Column(db.String(36))
    config = db.Column(mysql.MSMediumText, nullable=False)


class ConfigOutSchema(Schema):
    id = Integer()
    name = String()
    etag = String()
    config = String()


class EnvModel(db.Model):
    owner = db.Column(db.String(36), primary_key=True)
    repo = db.Column(db.String(36), primary_key=True)
    base_url = db.Column(db.String(36))
    issue_url = db.Column(db.String(36))
    pr_url = db.Column(db.String(36))


@app.get('/config')
@app.output(ConfigOutSchema(many=True))
def list_config():
    data = ConfigModel.query.all()
    return data


@app.post('/config')
@app.output(ConfigOutSchema, 201)
def add_config():
    with open('../.github/fabricbot.json') as f:
        config = json.load(f)
    data = {
        "id": 1,
        "name": "azure-cli.json",
        "etag": "a",
        "config": json.dumps(config)
    }
    db_data = ConfigModel(**data)
    db.session.add(db_data)
    db.session.commit()
    return db_data


if __name__ == '__main__':
    app.run()