import json
import httplib
from functools import wraps, partial

from flask import request
from wtforms import Form

from utils import failed_resp
from flaskApp import redis_client


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
    def __init__(self, login=None, auth=None, form=None):
        """
        :param login: verify login status
        :param auth: verify the access right of module
        :param form: verify request validation of form
        """
        self.auth = auth
        self.login = login
        if form is not None:
            assert isinstance(form, Form), "form must be subclass of wtforms.form.Form"
        self.form = form

    @staticmethod
    def authorization_check():
        return failed_resp("login required", httplib.UNAUTHORIZED)

    @staticmethod
    def permission_check():
        token = request.headers.get("Authorization", "").split(" ")[-1]
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
            if self.login:
                funcs.append(self.permission_check)
            if self.auth:
                funcs.append(self.authorization_check)
            if self.form:
                funcs.append(partial(self.form_check, self.form))
            for func in funcs:
                rv = func()
                if rv:
                    return rv
            return f(*args, **kwargs)
        return _decorate
