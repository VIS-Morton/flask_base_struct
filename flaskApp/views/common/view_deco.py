import json
from functools import wraps

from flask import request

from utils import failed_resp
from flaskApp import redis_client


def permission_check(func):
    @wraps(func)
    def _decorate(*args, **kwargs):
        token = request.headers.get("Authorization", "").split(" ")[-1]
        if not token:
            return failed_resp("Bearer access token missing", 401)
        access_token = "access-token" + token
        if not redis_client.exists(access_token):
            return failed_resp("login expired", 401)
        user_info = json.loads(redis_client.get(access_token))
        kwargs["user_info"] = user_info
        return func(*args, **kwargs)
    return _decorate
