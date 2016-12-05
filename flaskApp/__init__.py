# -*- coding:utf8 -*-
import re
import sys
import time

from flask import Flask, request
from flask_cors import CORS  # Cross Origin Resource sharing
from flask_pymongo import PyMongo
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from flask_wtf.csrf import CsrfProtect

from common.log import generate_logger_handler
from flaskApp.config import AppConfig
from models import db

socketio = SocketIO()
redis_client = FlaskRedis()  # Restrict redis
mongo_client = PyMongo()


def create_app(database, config="flaskApp.config.AppConfig"):
    app = Flask(__name__, root_path=AppConfig.ROOT_PATH)
    app.config.from_object(config)
    CORS(app)
    initialize_app(application=app, config=config)
    database.init_app(app)
    database.create_all(app=app)
    redis_client.init_app(app=app)
    mongo_client.init_app(app=app)
    app.logger_name = "app"
    app.logger.setLevel(10)
    app.logger.handlers = generate_logger_handler("app")   # handlers is a list

    add_request_handler(application=app, database=database)

    return app


def initialize_app(application, config, profile=False):
    if profile:
        from werkzeug.contrib.profiler import ProfilerMiddleware

        """
        请求性能测试参数说明：
            tottime : 在这个函数中所花费所有时间。
            percall : 是 tottime 除以 ncalls 的结果。
            cumtime : 花费在这个函数以及任何它调用的函数的时间。
            percall : cumtime 除以 ncalls。
            filename:lineno(function) : 函数名以及位置。
        """
        application.config['PROFILE'] = True
        application.wsgi_app = ProfilerMiddleware(application.wsgi_app, restrictions=[30])

    from flaskApp.views.apiView import api_view
    application.register_blueprint(api_view)

    csrf = CsrfProtect()
    csrf.init_app(application)
    csrf.exempt(api_view)       # escape csrf protect


def add_request_handler(application, database):
    @application.before_request
    def before_request():
        request.start_time = time.time()

    @application.after_request
    def after_request(response):
        start_time = getattr(request, "start_time", 0)
        use_time = 0
        if start_time:
            use_time = round((time.time() - start_time) * 1000, 3)
        method = request.method
        status_code = response.status_code
        url = re.sub("http://.*?/", "/", request.url)
        application.logger.info("%s %s %s-->cost:%s ms" % (method, status_code, url, use_time))
        return response

    @application.teardown_request
    def teardown_request(exception):
        database.session.close()  # make sure that db session is closed successfully
        if exception:
            start_time = getattr(request, "start_time", 0)
            use_time = 0
            if start_time:
                use_time = round((time.time() - start_time) * 1000, 3)
            method = request.method
            url = re.sub("http://.*?/", "/", request.url)
            form_data = {}
            form_data.update(request.form)
            form_data.update(request.args)
            application.logger.error("%s %s -->cost:%s ms, form_data: %s" % (url, method, use_time, str(form_data)))
            application.logger.error(exception, exc_info=1)
            sys.exc_clear()


app = create_app(db)