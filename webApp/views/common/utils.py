# -*- coding: utf-8 -*-
import httplib
from flask import jsonify, make_response


def succeed_resp(status_code=httplib.OK, **kwargs):
    return make_response(jsonify(response_code=1, message="success", **kwargs), status_code)


def failed_resp(message, status_code):
    return make_response(jsonify(message=message, response_code=0), status_code)
