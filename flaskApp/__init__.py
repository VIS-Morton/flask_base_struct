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
from celery import Celery

from common.log import generate_logger_handler, create_logger
from flaskApp.config import AppConfig
from models import db


socketio = SocketIO()
redis_client = FlaskRedis()  # Restrict redis
mongo_client = PyMongo()
celery = Celery(__name__, broker=AppConfig.CELERY_BROKER_URL)
# run celery : celery -A flaskApp.celery worker
# http://stackoverflow.com/questions/25884951/attributeerror-flask-object-has-no-attribute-user-options


def create_app(database, config="flaskApp.config.AppConfig"):
    app = Flask(__name__, root_path=AppConfig.ROOT_PATH)
    app.config.from_object(config)
    CORS(app)
    initialize_app(application=app)
    database.init_app(app)
    database.create_all(app=app)
    redis_client.init_app(app=app)
    mongo_client.init_app(app=app)
    if AppConfig.APP_SLOW_LOG:
        slow_logger_handler = generate_logger_handler("app-slow", is_stream_handler=False, add_error_log=False)
        app.slow_logger = create_logger("app-slow", handlers=slow_logger_handler)
    app.logger_name = "app"
    app.logger.setLevel(10)
    app.logger.handlers = generate_logger_handler("app")   # handlers is a list

    add_request_handler(application=app, database=database)  # register request handler
    initialize_celery(celery, application=app)

    return app


def initialize_app(application, profile=False):
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
    def write_slow_log(start_time, use_time, status_code):
        if AppConfig.APP_SLOW_LOG:
            if use_time > AppConfig.APP_SLOW_LOG:
                form_data = {}
                form_data.update(request.form)
                form_data.update(request.args)
                application.slow_logger.info("%s %s %s-->start time:%s, use: %s ms, form data: %s" % (
                    request.method, status_code, request.path, start_time, use_time, str(form_data)))


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
        path = request.path
        application.logger.info("%s %s %s-->cost:%s ms" % (method, status_code, path, use_time))
        write_slow_log(start_time, use_time, status_code)
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
            write_slow_log(start_time, use_time, 500)
            sys.exc_clear()





def initialize_celery(celery, application):
    celery.conf.update(application.config)
    BaseTask = celery.Task

    class ContextTask(BaseTask):
        abstract = True

        def __call__(self, *args, **kwargs):
            with application.app_context():
                return BaseTask.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = create_app(db)


from celleryBackgound import trigger_celery


@app.route("/test")
def test():
    import time
    time.sleep(5.1)
    trigger_celery.apply_async(("test", 1), countdown=5)
    return "hello world, celery trigger success"
