from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_apscheduler import APScheduler


db = SQLAlchemy()
cache = Cache()
scheduler = APScheduler()