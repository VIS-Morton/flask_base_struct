from flask import Blueprint

from flask_restful import Api

rest_api_view = Blueprint("rest_api_view", __name__, url_prefix="/api")
restful_api = Api(rest_api_view)

from sampleApi import SimpleResource

restful_api.add_resource(SimpleResource, "/samples", "/samples/<int:id>")


