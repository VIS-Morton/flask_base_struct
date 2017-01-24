from flask import request, session, jsonify, render_template, redirect, url_for
import flask_login

from form import LoginForm
from webApp import app, csrf
from webApp.models import User
from webApp.extension import login_manager
from webApp.views.common.middelware import SecureMiddleWare


@app.route("/login", methods=["GET", "POST"], endpoint="login")
@csrf.exempt
@SecureMiddleWare(form=LoginForm, allowed_methods=[])
def login():
    if request.method == "POST" or True:
        username = request.validate_form.username.data
        password = request.validate_form.password.data
        user_row = User.get_user(username, password)
        if user_row:
            user_row.id = unicode(user_row.uid)
            flask_login.login_user(user_row)
            return jsonify(username=user_row.username, uid=user_row.uid,
                           auth_token=flask_login.make_secure_token())
            next_url = request.validate_form.next_url.data
            return redirect(next_url or url_for("login"))
        return jsonify(message="error username or password")
    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"], endpoint="logout")
@csrf.exempt
@flask_login.login_required
def logout():
    print 1
    uid = session.get("user_id")
    flask_login.logout_user()
    return jsonify(uid=uid)
