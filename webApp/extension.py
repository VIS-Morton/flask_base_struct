from flask_pymongo import PyMongo
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_wtf.csrf import CsrfProtect
from celery import Celery


from webApp.config import AppConfig


class FlaskCelery(Celery):
    def init_app(self, app):
        self.conf.update(app.config)
        BaseTask = self.Task

        class ContextTask(BaseTask):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return BaseTask.__call__(self, *args, **kwargs)
        self.Task = ContextTask


db = SQLAlchemy()
socketio = SocketIO()
redis_client = FlaskRedis()  # Restrict redis
mongo_client = PyMongo()
login_manager = LoginManager()
csrf = CsrfProtect()
cors = CORS()
celery = FlaskCelery(__name__, broker=AppConfig.CELERY_BROKER_URL)
# run celery : celery -A module-name.celery worker
# http://stackoverflow.com/questions/25884951/attributeerror-flask-object-has-no-attribute-user-options