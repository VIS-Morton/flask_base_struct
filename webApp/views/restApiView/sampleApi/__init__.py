from flask_restful import Resource

from webApp.models import Sample
from webApp.views.common.utils import failed_resp, succeed_resp
from form import *


class SimpleResource(Resource):
    def get(self, id=None):
        if id:
            sample = Sample.query.get(id)
        else:
            sample = Sample.query.first()
        if sample:
            return succeed_resp(sample={"id": sample.id})
        return failed_resp("no such sample", 200)

