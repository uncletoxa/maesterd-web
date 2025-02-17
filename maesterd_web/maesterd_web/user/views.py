import sqlalchemy as sa
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required
from maesterd_web.extensions import db
from maesterd_web.story.models import Story
from maesterd_web.user.models import User
from maesterd_web.settings import STORIES_PER_PAGE

blueprint = Blueprint("user", __name__, url_prefix="/user", static_folder="static")


@blueprint.route('/<username>')
@login_required
def user_profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = sa.select(Story).where(Story.user_id==user.user_id).order_by(Story.created_at.desc())
    stories = db.paginate(query, page=page, per_page=STORIES_PER_PAGE, error_out=False)
    next_url = url_for('user_profile', page=stories.next_num) if stories.has_next else None
    prev_url = url_for('user_profile', page=stories.prev_num) if stories.has_prev else None

    return render_template('user/profile.html', user=user,
                           stories=stories.items, next_url=next_url, prev_url=prev_url)
