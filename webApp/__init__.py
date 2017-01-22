# -*- coding:utf8 -*-
import re
import sys
import time
from logging import Formatter

from werkzeug.wrappers import Response
from flask import Flask, request, jsonify
from flask_sqlalchemy import get_debug_queries

from common.log import generate_logger_handler, create_logger
from webApp.config import AppConfig
from extension import db, redis_client, mongo_client, socketio, login_manager, csrf, cors, celery


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)
        return super(JsonResponse, cls).force_type(response, environ)


app = Flask(__name__, root_path=AppConfig.ROOT_PATH)


def initialize_app(application, profile=False, config="webApp.config.AppConfig"):
    app.config.from_object(config)
    db.init_app(app)
    db.drop_all(app=app)
    db.create_all(app=app)
    redis_client.init_app(app=app)
    mongo_client.init_app(app=app)
    login_manager.init_app(app=app)
    csrf.init_app(app=app)
    cors.init_app(app=app)
    celery.init_app(app=app)
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

    from views.restApiView import rest_api_view
    import views.generalApiView

    application.register_blueprint(rest_api_view)

    csrf.exempt(rest_api_view)       # escape csrf protect


    if AppConfig.APP_SLOW_LOG:
        slow_logger_handler = generate_logger_handler("app-slow", is_stream_handler=False,
                                                      add_error_log=False, formatter=Formatter("%(asctime)s %(message)s"))
        app.slow_logger = create_logger("app-slow", handlers=slow_logger_handler)
    app.logger_name = "app"
    app.logger.setLevel(10)
    app.logger.handlers = generate_logger_handler("app")   # handlers is a list

    add_request_handler(application=app, database=db)  # register request handler


def add_request_handler(application, database):
    def write_slow_log(start_time, use_time, status_code):
        if AppConfig.APP_SLOW_LOG:
            index = 0
            for index, query in enumerate(get_debug_queries()):
                application.slow_logger.info(
                    "\nContext: {}\nQuery: {}\nParameters: {}\nDuration:{}\n".format(
                        query.context, query.statement, query.parameters, query.duration))
            if use_time > AppConfig.REQUEST_SLOW_TIME:
                form_data = {}
                form_data.update(request.form)
                form_data.update(request.args)
                application.slow_logger.info("%s %s %s-->use: %s ms, query times: %s form data: %s " %
                                             (request.method, status_code, request.path,
                                              use_time, index + 1, str(form_data)))

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
            application.logger.error("%s %s -->cost:%s ms, form data: %s" % (url, method, use_time, str(form_data)))
            application.logger.error(exception, exc_info=1)
            write_slow_log(start_time, use_time, 500)
            sys.exc_clear()


initialize_app(app)