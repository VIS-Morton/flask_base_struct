from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired, Length


class LoginForm(Form):
    class UserForm(Form):
        username = StringField(validators=[InputRequired(), Length(min=6, max=30)])
        password = PasswordField(validators=[InputRequired(), Length(min=8, max=30)])