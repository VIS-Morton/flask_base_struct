import json
import httplib
from functools import wraps, partial

from flask import request
from wtforms import Form
from flask_login import UserMixin

from webApp.config import AppConfig
from webApp.extension import redis_client
from utils import failed_resp


def permission_check(func):
    @wraps(func)
    def _decorate(*args, **kwargs):
        token = request.headers.get("Authorization", "").split(" ")[-1]
        if not token:
            return failed_resp("Bearer access token missing", httplib.UNAUTHORIZED)
        access_token = "access-token" + token
        if not redis_client.exists(access_token):
            return failed_resp("login expired", httplib.UNAUTHORIZED)
        user_info = json.loads(redis_client.get(access_token))
        kwargs["user_info"] = user_info
        return func(*args, **kwargs)
    return _decorate


class SecureMiddleWare(object):
    def __init__(self, form=None, allowed_methods=None):
        """
        :param form: verify request validation of form
        """
        if form is not None:
            assert issubclass(form, Form), "form must be subclass of wtforms.form.Form"
        self.form = form
        if allowed_methods is not None:
            assert isinstance(allowed_methods, list), "allowed_methods must be a list"
        self.allowed_methods = [] if allowed_methods is None else map(lambda i: i.upper(), allowed_methods)

    @staticmethod
    def permission_check():
        token = request.headers.get(AppConfig.AUTH_HEADER_NAME, "").split(" ")[-1]
        if not token:
            return failed_resp("Bearer access token missing", httplib.UNAUTHORIZED)
        access_token = "access-token" + token
        if not redis_client.exists(access_token):
            return failed_resp("login required", httplib.UNAUTHORIZED)
        request.user_info = json.loads(redis_client.get(access_token))

    @staticmethod
    def form_check(Form):
        if request.method == "GET":
            form = request.args
        else:
            form = request.form
        form = Form(form)
        if form.validate():
            request.validate_form = form
            return
        for error_filed, error_message in form.errors.iteritems():
            if isinstance(error_message, list) and error_message:
                error_message = error_message[0]
            return failed_resp("%s: %s" % (error_filed, error_message), httplib.BAD_REQUEST)

    def __call__(self, f):
        def _decorate(*args, **kwargs):
            funcs = []
            if self.form:
                if request.method not in self.allowed_methods:
                    funcs.append(partial(self.form_check, self.form))
            for func in funcs:
                rv = func()
                if rv:
                    return rv
            return f(*args, **kwargs)
        return _decorate
