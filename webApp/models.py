# -*- coding: utf-8 -*-
import time
from hashlib import md5

from sqlalchemy import INTEGER, VARCHAR, TEXT, TIMESTAMP, func, SMALLINT

from extension import db


class Sample(db.Model):
    __tablename__ = "sample"

    id = db.Column("id", INTEGER, primary_key=True, nullable=False, autoincrement=True)

    def __init__(self):
        pass


# Example
#class User(db.Model):
class User(object):
    __tablename__ = "user"

    IN_SERVICE = 1
    OUT_SERVICE = 0
    DEFAULT_PARENT_ID = 0

    uid = db.Column("uid", INTEGER, primary_key=True, nullable=False, autoincrement=True)
    username = db.Column("username", VARCHAR(length=64), nullable=False, unique=True)
    password = db.Column("password", VARCHAR(length=64), nullable=False)
    salt = db.Column("salt", VARCHAR(length=64), nullable=False)
    email = db.Column("email", VARCHAR(length=255), nullable=True, unique=True)
    parent_id = db.Column("parent_id", INTEGER, nullable=False, server_default=str(DEFAULT_PARENT_ID),
                          doc="0:no parent")
    roles = db.Column("roles", VARCHAR(length=255), nullable=False, server_default="",
                      doc="user roles, split by ';'")
    register_time = db.Column("register_time", TIMESTAMP, server_default=func.now(), nullable=False)
    last_login_time = db.Column("last_login_time", TIMESTAMP, server_default=func.now(),
                                nullable=False, onupdate=func.now())
    status = db.Column("status", SMALLINT, server_default=str(IN_SERVICE), doc="1:in service 0:out of service")
    option = db.Column("option", TEXT(65535), nullable=True, doc="default recognize option;json;lower priority")

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def get_salt(cls):
        salt = md5(str(time.time())).hexdigest()
        return salt

    @classmethod
    def encrypt_password(cls, password, salt):
        password = md5("courage-{}-blood".format(password)).hexdigest()
        return md5(password + salt).hexdigest()

    @classmethod
    def generate_auth_token(cls, password):
        return md5("concentration-{}-insistence".format(password)).hexdigest()

    @classmethod
    def get_user(cls, username, password):
        user_row = cls.query.filter_by(username=username).first()
        if user_row:
            password = cls.encrypt_password(password, salt=user_row.salt)
            if password == user_row.password:
                return user_row
        return None
