import logging
import sqlalchemy as sa
from uuid import uuid4

from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from maesterd_web.extensions import db
from maesterd_web.story.models import Story, Chapter
from maesterd_web.story.forms import StoryForm, ChapterForm
from maesterd_web.utils.requests import make_request, SocketRequestError
from maesterd_web.settings import CHAPTERS_PER_PAGE

logger = logging.getLogger(__name__)
blueprint = Blueprint("story", __name__, url_prefix="/story", static_folder="static")


def handle_story_request(request_type: str, form_data: dict, story_id=None):
    """
    Handle socket requests for story creation and continuation.
    Returns (success, redirect_url) tuple.
    """
    try:
        request_data = {"type": request_type,
                        "thread_id": f"user={current_user.user_id}.thread={story_id or uuid4()}",
                        "api_key": form_data['api_key']}

        if request_type == "new_story":
            request_data["description"] = form_data['description']
        elif request_type == "continue_story":
            request_data.update({
                "prompt": form_data['prompt'],
                "chapter_number": form_data['chapter_number']})

        response = make_request(socket_path=current_app.config["OPENAI_SOCKET_ADDR"],
                                request_data=request_data)

        if "error" in response:
            raise SocketRequestError(response["error"])

        if request_type == "new_story":
            st = Story(story_id=story_id or uuid4(),
                       title=response["name"],
                       setting=response["setting"],
                       goal=response["goal"],
                       description=form_data['description'],
                       user_id=current_user.user_id,
                       response=response.get("initial_response", ""))
            db.session.add(st)
            flash('Your story is now live!')

        elif request_type == "continue_story":
            chapter = Chapter(prompt=form_data['prompt'],
                              response=response["content"],
                              chapter_number=form_data['chapter_number'],
                              story_id=story_id)
            db.session.add(chapter)
            flash('New chapter is now live!', 'success')

        db.session.commit()
        return True, url_for('story.story', story_id=story_id)

    except SocketRequestError as e:
        logger.error("Socket communication error: %s", e)
        flash('Unable to communicate with story service. Please try again later.', 'error')
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        db.session.rollback()
        flash('An unexpected error occurred. Please try again.', 'error')

    return False, url_for('story.new' if request_type == "new_story" else 'story.story', story_id=story_id)


@blueprint.route('/<uuid:story_id>', methods=['GET', 'POST'])
@login_required
def story(story_id):
    story = db.first_or_404(sa.select(Story).where(Story.story_id==story_id))
    chapters_query = sa.select(Chapter).where(Chapter.story_id==story.story_id).order_by(Chapter.chapter_number)
    chapters = db.session.scalars(chapters_query)
    form = ChapterForm()

    if form.validate_on_submit():
        success, redirect_url = handle_story_request(
            request_type='continue_story',
            form_data={'prompt': form.prompt.data,
                       'api_key': form.api_key.data,
                       'chapter_number': len(list(chapters)) + 1},
            story_id=story_id)
        return redirect(redirect_url)

    return render_template('story/story.html', chapters=chapters, story=story, form=form)

@blueprint.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = StoryForm()
    if form.validate_on_submit():
        success, redirect_url = handle_story_request(
            request_type="new_story",
            form_data={'description': form.description.data,
                       'api_key': form.api_key.data})
        return redirect(redirect_url)
    return render_template('story/new.html', title='New Story', form=form)
