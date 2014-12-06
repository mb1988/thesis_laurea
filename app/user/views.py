#viste di login e logout

from flask import Blueprint, request, render_template, redirect,url_for
from flask.ext import login

from app import db
from app.user.forms import LoginForm
from app.user.models import User
from app.admin import *

users = Blueprint('users',__name__)

@users.route('/', methods=('GET', 'POST'))
def index():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = form.get_user()
        login.login_user(user)
        return redirect(url_for('admin.index'))

    return render_template('login.html', form=form)

@users.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('.index'))
    

