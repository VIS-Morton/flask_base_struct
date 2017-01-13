from flask import Blueprint

from flask_restful import Api

api_view = Blueprint("api_view", __name__, url_prefix="/api")
restful_api = Api(api_view)

from userApi import UserResource

restful_api.add_resource(UserResource, "/users", "/users/<int:uid>")


