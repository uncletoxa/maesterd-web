import sqlalchemy as sa
from flask_login import current_user, login_user
from maesterd_web.models import User
from .forms import LoginForm
from maesterd_web.auth import bp
from flask import render_template, redirect, url_for, flash, request



@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)
