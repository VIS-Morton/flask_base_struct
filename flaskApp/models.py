# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import INTEGER, VARCHAR, TEXT, TIMESTAMP, func, Enum, DATETIME

from extension import db


class User(db.Model):
    __tablename__ = "user"

    uid = db.Column("uid", INTEGER, primary_key=True, nullable=False, autoincrement=True)
    raw_uid = db.Column("raw_uid", INTEGER, nullable=True, default=-1)
    username = db.Column("username", VARCHAR(length=64), nullable=False, unique=True)
    password = db.Column("password", VARCHAR(length=64), nullable=False)
    email = db.Column("email", VARCHAR(length=255), nullable=True, unique=True)
    parent_id = db.Column("parent_id", INTEGER, nullable=False, default=0, doc="0:no parent")
    roles = db.Column("roles", VARCHAR(length=255), nullable=False, default="", doc="user roles, split by ';'")
    register_time = db.Column("register_time", TIMESTAMP, server_default=func.now(), nullable=False)
    last_login_time = db.Column("last_login_time", TIMESTAMP, server_default=func.now(), nullable=False,
                                onupdate=func.now())
    status = db.Column("status", INTEGER, default=1, doc="1:in service 2:out of service")
    option = db.Column("option", TEXT(65535), nullable=True, doc="default recognize option;json;lower priority")

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)