import sqlalchemy as sa

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from maesterd_web.extensions import db
from maesterd_web.story.models import Story, Chapter
from maesterd_web.story.forms import StoryForm, ChapterForm
from maesterd_web.utils.requests import make_request


blueprint = Blueprint("story", __name__, url_prefix="/story", static_folder="static")


@blueprint.route('/<int:story_id>', methods=['GET', 'POST'])
@login_required
def story(story_id):
    story = db.first_or_404(sa.select(Story).where(Story.story_id == story_id))
    chapters_query = sa.select(Chapter).where(Chapter.story_id == story.story_id).order_by(Chapter.chapter_number)
    chapters = db.session.scalars(chapters_query)
    form = ChapterForm()

    if form.validate_on_submit():
        try:
            all_chapters = list(chapters)
            chapter = Chapter(
                prompt=form.prompt.data,
                chapter_number=len(all_chapters) + 1,
                story_id=story_id
            )

            # Try to make the OpenAI request
            try:
                chapter.response = make_request(chapter.prompt, form.api_key.data)
            except Exception as e:
                flash('An unexpected error occurred. Please try again.', 'error')
                return redirect(url_for('story', story_id=story_id))

            db.session.add(chapter)
            db.session.commit()
            flash('New chapter is now live!', 'success')

        except Exception as e:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')

        return redirect(url_for('story.story', story_id=story_id))

    return render_template('story/story.html', chapters=chapters, story=story, form=form)


@blueprint.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = StoryForm()
    if form.validate_on_submit():
        story = Story(title=form.title.data, description=form.description.data, user_id=current_user.user_id)
        db.session.add(story)
        db.session.commit()
        flash('Your story is now live!')
        return redirect(url_for('story.new', story_id=story.story_id))
    return render_template('story/new.html', title='New Story', form=form)
