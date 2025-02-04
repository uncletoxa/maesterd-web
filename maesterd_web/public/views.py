from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from maesterd_web import app, db
from maesterd_web.public.forms import LoginForm, RegistrationForm, StoryForm, ChapterForm
from maesterd_web.models import User, Story, Chapter
from maesterd_web.settings import STORIES_PER_PAGE, CHAPTERS_PER_PAGE

from openai import OpenAI, OpenAIError
import requests.exceptions


@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Story).where(Story.user_id==current_user.user_id).order_by(Story.created_at.desc())
    stories = db.paginate(query, page=page, per_page=STORIES_PER_PAGE, error_out=False)
    next_url = url_for('index', page=stories.next_num) if stories.has_next else None
    prev_url = url_for('index', page=stories.prev_num) if stories.has_prev else None

    return render_template("index.html", title='Home Page',
                           stories=stories.items, next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)