import json
import httplib

from flask import request, make_response, jsonify
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
# celery -A webApp.celery  worker
# http://stackoverflow.com/questions/25884951/attributeerror-flask-object-has-no-attribute-user-options


def load_user(user_id):
    token = request.headers.get(AppConfig.AUTH_HEADER_NAME, "").split(" ")[-1]
    if not token:
        return make_response(jsonify(message="Bearer access token missing", code=0), httplib.UNAUTHORIZED)
    access_token = "access-token-{}-{}".format(user_id, token)
    if not redis_client.exists(access_token):
        return make_response(jsonify(message="login expired", code=0), httplib.UNAUTHORIZED)
    return json.loads(redis_client.get(access_token))

login_manager.user_callback = load_user
