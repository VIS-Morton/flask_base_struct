from flask import Blueprint

from flask_restful import Api

rest_api_view = Blueprint("rest_api_view", __name__, url_prefix="/api")
restful_api = Api(rest_api_view)

from userApi import UserResource

restful_api.add_resource(UserResource, "/users", "/users/<int:uid>")


