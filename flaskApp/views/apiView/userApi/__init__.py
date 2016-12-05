from flask_restful import Resource

from flaskApp.models import User
from flaskApp.views.common.utils import failed_resp, succeed_resp
from form import *


class UserResource(Resource):
    def get(self, uid=None):
        rows = []
        if not uid:
            rows = User.query.filter_by(status=1)
        else:
            row = User.query.filter_by(uid=uid, status=1).first()
            if row:
                rows.append(row)

        new_user_info = []
        for row in rows:
            if not row.roles:
                return failed_resp("account has no roles", 200)
            role_lst = map(int, row.roles.split(";"))
            new_user_info.append({"uid": row.uid, "username": row.username, "roles": role_lst})
        
        if len(new_user_info) > 0:
            return succeed_resp(user_info=new_user_info)
        return failed_resp("account out of service", 200)

