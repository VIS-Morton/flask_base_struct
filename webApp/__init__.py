# -*- coding:utf8 -*-
from flask import Flask
from logging import Formatter
from webApp.config import AppConfig

app = Flask(__name__, root_path=AppConfig.ROOT_PATH)

import preprocessor
from common.log import generate_logger_handler, create_logger
from extension import db, redis_client, mongo_client, socketio, login_manager, csrf, cors, celery
from views.restApiView import rest_api_view
import views.generalApiView


def initialize_app(app, profile=False, config="webApp.config.AppConfig"):
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
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    app.register_blueprint(rest_api_view)

    csrf.exempt(rest_api_view)       # escape csrf protect

    if AppConfig.APP_SLOW_LOG:
        slow_logger_handler = generate_logger_handler("app-slow", is_stream_handler=False, add_error_log=False,
                                                      formatter=Formatter("%(asctime)s %(message)s"))
        app.slow_logger = create_logger("app-slow", handlers=slow_logger_handler)
    app.logger_name = "app"
    app.logger.setLevel(10)
    app.logger.handlers = generate_logger_handler("app")   # handlers is a list


initialize_app(app)
preprocessor.write_preset_data()
