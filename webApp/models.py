# -*- coding: utf-8 -*-
import time
from hashlib import md5

from sqlalchemy import INTEGER, VARCHAR, TIMESTAMP, func, SMALLINT, Index
from flask_login import UserMixin

from extension import db


class User(db.Model, UserMixin):
    __tablename__ = "user"

    IN_SERVICE = 1
    OUT_SERVICE = 0
    DEFAULT_PARENT_ID = 0  # 0 means having no parent

    uid = db.Column("uid", INTEGER, primary_key=True, nullable=False, autoincrement=True)
    username = db.Column("username", VARCHAR(length=64), nullable=False)
    password = db.Column("password", VARCHAR(length=64), nullable=False)
    salt = db.Column("salt", VARCHAR(length=64), nullable=False)
    email = db.Column("email", VARCHAR(length=255), nullable=False, server_default="")
    parent_id = db.Column("parent_id", INTEGER, nullable=False, server_default=str(DEFAULT_PARENT_ID),
                          doc="0:no parent")
    roles = db.Column("roles", VARCHAR(length=255), nullable=False, server_default="",
                      doc="user roles, split by ';'")
    register_time = db.Column("register_time", TIMESTAMP, server_default=func.now(), nullable=False)
    last_login_time = db.Column("last_login_time", TIMESTAMP, server_default=func.now(),
                                nullable=False, onupdate=func.now())
    active = db.Column("active", SMALLINT, server_default=str(IN_SERVICE), nullable=False,
                       doc="1:in service 0:out of service")

    usernameIndex = Index("username", username, unique=True)
    emailIndex = Index("email", email, unique=True)

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
        user_row = cls.query.filter_by(username=username, active=cls.IN_SERVICE).first()
        if user_row:
            password = cls.encrypt_password(password, salt=user_row.salt)
            if password == user_row.password:
                return user_row
        return None


class Role(db.Model):
    __tablename__ = "role"

    IN_SERVICE = 1
    OUT_SERVICE = 0

    role_id = db.Column("role_id", INTEGER, primary_key=True, nullable=False, autoincrement=True,
                        doc="value is 1 means it is admin which has all permissions")
    role_name = db.Column("role_name", VARCHAR(255), nullable=False)
    permissions = db.Column("permissions", VARCHAR(255), nullable=False, default="", doc="split by ';'")
    active = db.Column("active", SMALLINT, server_default=str(IN_SERVICE), nullable=False,
                       doc="1:in service 0:out of service")
    create_time = db.Column("create_time", TIMESTAMP, nullable=False, server_default=func.now())
    update_time = db.Column("update_time", TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def get_permissions(cls, roles):
        if isinstance(roles, str):
            roles = map(int, roles.split(";"))
        elif isinstance(roles, int):
            roles = [roles]
        assert isinstance(roles, (list, tuple))
        role_rows = cls.query.filter(cls.role_id.in_(roles), cls.active==cls.IN_SERVICE).all()
        permissions = []
        for role_row in role_rows:
            if role_row.permissions:
                permissions.extend(map(int, role_row.permissions.split(";")))
        return tuple(set(permissions))


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
    active = db.Column("active", SMALLINT, nullable=False, server_default=str(IN_SERVICE),
                       doc="1:in service 0:out of service")
    create_time = db.Column("create_time", TIMESTAMP, nullable=False, server_default=func.now())
    update_time = db.Column("update_time", TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
