from flask_pymongo import PyMongo
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from celery import Celery


from flaskApp.config import AppConfig


db = SQLAlchemy()
socketio = SocketIO()
redis_client = FlaskRedis()  # Restrict redis
mongo_client = PyMongo()
login_manager = LoginManager()
celery = Celery(__name__, broker=AppConfig.CELERY_BROKER_URL)
# run celery : celery -A module-name.celery worker
# http://stackoverflow.com/questions/25884951/attributeerror-flask-object-has-no-attribute-user-options