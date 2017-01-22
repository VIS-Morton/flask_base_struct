# -*- coding: utf8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import Length, InputRequired


class UserForm(Form):
    username = StringField(validators=[InputRequired(), Length(min=6, max=30)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=30)])


class CreateUserForm(UserForm):
    roles = StringField(validators=[InputRequired(), Length(min=1, max=100)])