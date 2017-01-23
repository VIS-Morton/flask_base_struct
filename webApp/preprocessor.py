import re
import sys
import time
from flask import request, jsonify
from flask_sqlalchemy import get_debug_queries
from werkzeug.wrappers import Response

from webApp import app
from models import User, Role, db
from config import AppConfig


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)
        return super(JsonResponse, cls).force_type(response, environ)


def write_preset_data():
    with app.app_context():
        salt = User.get_salt()
        password = User.encrypt_password("12345678", salt)
        user = User(uid=1, username="admin@viscovery.cn", password=password, salt=salt, roles="1")
        role = Role(role_id=1, role_name="administrator")
        db.session.add(user)
        db.session.add(role)
        db.session.commit()
        db.session.close()


def write_slow_log(start_time, use_time, status_code):
    if AppConfig.APP_SLOW_LOG:
        index = 0
        for index, query in enumerate(get_debug_queries()):
            # db slow query log
            app.slow_logger.info(
                "\nContext: {}\nQuery: {}\nParameters: {}\nDuration:{}\n".format(
                    query.context, query.statement, query.parameters, query.duration))
        if use_time > AppConfig.REQUEST_SLOW_TIME:
            # request slow log
            form_data = {}
            form_data.update(request.form)
            form_data.update(request.args)
            app.slow_logger.info("%s %s %s-->use: %s ms, query times: %s form data: %s " %
                                 (request.method, status_code, request.path, use_time, index + 1, str(form_data)))


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    start_time = getattr(request, "start_time", 0)
    use_time = 0
    if start_time:
        use_time = round((time.time() - start_time) * 1000, 3)
    method = request.method
    status_code = response.status_code
    path = request.path
    app.logger.info("%s %s %s-->cost:%s ms" % (method, status_code, path, use_time))
    write_slow_log(start_time, use_time, status_code)
    return response


@app.teardown_request
def teardown_request(exception):
    db.session.close()  # make sure that db session is closed successfully
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
        app.logger.error("%s %s -->cost:%s ms, form data: %s" % (url, method, use_time, str(form_data)))
        app.logger.error(exception, exc_info=1)
        write_slow_log(start_time, use_time, 500)
        sys.exc_clear()