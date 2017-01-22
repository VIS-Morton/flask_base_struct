# -*- coding: utf-8 -*-
from hashlib import md5

from sqlalchemy import INTEGER, VARCHAR, TEXT, TIMESTAMP, func, SMALLINT

from extension import db


class User(db.Model):
    __tablename__ = "user"

    IN_SERVICE = 1
    OUT_SERVICE = 0

    uid = db.Column("uid", INTEGER, primary_key=True, nullable=False, autoincrement=True)
    username = db.Column("username", VARCHAR(length=64), nullable=False, unique=True)
    password = db.Column("password", VARCHAR(length=64), nullable=False)
    email = db.Column("email", VARCHAR(length=255), nullable=True, unique=True)
    parent_id = db.Column("parent_id", INTEGER, nullable=False, default=0, doc="0:no parent")
    roles = db.Column("roles", VARCHAR(length=255), nullable=False, default="", doc="user roles, split by ';'")
    register_time = db.Column("register_time", TIMESTAMP, server_default=func.now(), nullable=False)
    last_login_time = db.Column("last_login_time", TIMESTAMP, server_default=func.now(),
                                nullable=False, onupdate=func.now())
    status = db.Column("status", SMALLINT, server_default=str(IN_SERVICE), doc="1:in service 0:out of service")
    option = db.Column("option", TEXT(65535), nullable=True, doc="default recognize option;json;lower priority")

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def encode_password(cls, password):
        return md5("courage-{}-blood".format(password)).hexdigest()

    @classmethod
    def get_user(cls, username, password):
        password = cls.encode_password(password)
        return cls.query.filter_by(username=username, password=password).first()


class Role(db.Model):
    __tablename__ = "role"

    IN_SERVICE = 1
    OUT_SERVICE = 0

    role_id = db.Column("role_id", INTEGER, primary_key=True, nullable=False, autoincrement=True,
                        doc="value is 1 means it is admin which has all permissions")
    role_name = db.Column("role_name", VARCHAR(255), nullable=False)
    permissions = db.Column("permissions", VARCHAR(255), nullable=False, default="", doc="split by ';'")
    status = db.Column("status", SMALLINT, server_default=str(IN_SERVICE), nullable=False,
                       doc="1:in service 0:out of service")
    create_time = db.Column("create_time", TIMESTAMP, nullable=False, server_default=func.now())
    update_time = db.Column("update_time", TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Permission(db.Model):
    """
    permission of module, control the access of url
    """
    __tablename__ = "permission"

    IN_SERVICE = 1
    OUT_SERVICE = 0

    permission_id = db.Column("permission_id", INTEGER, primary_key=True, nullable=False, autoincrement=True)
    permission_name = db.Column("permission_name", VARCHAR(255), nullable=False)
    parent_id = db.Column("parent_id", INTEGER, nullable=False, server_default=str(0),
                          doc="0:no parent; root")
    url = db.Column("url", VARCHAR(255), nullable=False, server_default="",
                    doc="full url route of the permission;"
                        "null for root module, parent of the permission which has url")
    status = db.Column("status", SMALLINT, nullable=False, server_default=str(IN_SERVICE),
                       doc="1:in service 0:out of service")
    create_time = db.Column("create_time", TIMESTAMP, nullable=False, server_default=func.now())
    update_time = db.Column("update_time", TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
