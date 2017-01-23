from flask import request, jsonify, render_template, redirect, url_for
from flask_login import login_user

from form import LoginForm
from webApp import app, csrf
from webApp.models import User
from webApp.views.common.middelware import SecureMiddleWare, UserMiddleware, permission_check


@app.route("/login", methods=["GET", "POST"], endpoint="login")
@csrf.exempt
@SecureMiddleWare(form=LoginForm, allowed_methods=["GET"])
def login():
    if request.method == "POST":
        username = request.validate_form.username.data
        password = request.validate_form.password.data
        user_row = User.get_user(username, password)
        user = UserMiddleware(user_row)
        login_user(user)
        return jsonify(username=user_row.username, uid=user_row.uid)
        next_url = request.validate_form.next_url.data
        return redirect(next_url or url_for("login"))
    return render_template("login.html", form=request.args)


@app.route("/logout", methods=["GET", "POST"], endpoint="logout")
@SecureMiddleWare()
def logout():
    pass
