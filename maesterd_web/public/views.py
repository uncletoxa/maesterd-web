import sqlalchemy as sa

from flask import Blueprint, render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
from flask_login import current_user, login_user, logout_user, login_required
from maesterd_web.extensions import db, login
from maesterd_web.settings import STORIES_PER_PAGE
from maesterd_web.public.forms import LoginForm, RegistrationForm
from maesterd_web.user.models import User
from maesterd_web.story.models import Story


blueprint = Blueprint("public", __name__, static_folder="static")


@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@blueprint.route('/')
@blueprint.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Story).where(Story.user_id==current_user.user_id).order_by(Story.created_at.desc())
    stories = db.paginate(query, page=page, per_page=STORIES_PER_PAGE, error_out=False)
    next_url = url_for('public.index', page=stories.next_num) if stories.has_next else None
    prev_url = url_for('public.index', page=stories.prev_num) if stories.has_prev else None

    return render_template("public/index.html", title='Home Page',
                           stories=stories.items, next_url=next_url, prev_url=prev_url)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('public.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('public.index')
        return redirect(next_page)
    return render_template('public/login.html', title='Sign In', form=form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('public.login'))
    return render_template('public/register.html', title='Register', form=form)
