import logging
import uuid

import sqlalchemy as sa
from uuid import UUID

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from maesterd_web.extensions import db
from maesterd_web.story.models import Story, Chapter
from maesterd_web.story.forms import StoryForm, ChapterForm

from langchain_core.messages import HumanMessage
from maesterd.llm.graph import graph
from maesterd.constants import GRAPH_RECURSION_LIMIT


logger = logging.getLogger(__name__)
blueprint = Blueprint("story", __name__, url_prefix="/story", static_folder="static")


@blueprint.route('/<uuid:story_id>', methods=['GET', 'POST'])
@login_required
def story(story_id):
    story = db.first_or_404(sa.select(Story).where(Story.story_id == story_id))  # noqa
    chapters_query = sa.select(Chapter).where(Chapter.story_id == story.story_id).order_by(Chapter.chapter_number)  # noqa
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
                config = {
                    "recursion_limit": GRAPH_RECURSION_LIMIT,
                    "num_pc": 1,
                    "configurable": {
                        "thread_id": f"user={current_user.user_id}.thread={story_id}"
                    }
                }

                graph.update_state(
                    config=config,
                    values={
                        'actor_prompts': [chapter.prompt],
                        "num_pc": 1,
                    }
                )  # update with prompt
                _ = graph.invoke(input={'actor_prompts': [chapter.prompt]}, config=config)  # continue execution
                chapter.response = graph.get_state(config=config).values['messages'][-1].content

            except Exception as e:
                logger.error(f"Error occurred: {e}")
                flash('An unexpected error occurred. Please try again.', 'error')
                return redirect(url_for('story', story_id=story_id))

            db.session.add(chapter)
            db.session.commit()
            flash('New chapter is now live!', 'success')

        except Exception:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')

        return redirect(url_for('story.story', story_id=story_id))

    return render_template('story/story.html', chapters=chapters, story=story, form=form)


@blueprint.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = StoryForm()
    if form.validate_on_submit():

        story_id = uuid.uuid4()
        config = {
            "recursion_limit": GRAPH_RECURSION_LIMIT,
            "configurable": {
                "thread_id": f"user={current_user.user_id}.thread={story_id}"
            }
        }
        messages = [
            HumanMessage(
                content=f"Description: {form.description.data}",
                author_id=current_user.user_id
            )
        ]
        r = graph.invoke(
            input={"messages": messages, 'num_pc': 1},  # TODO: for now only 1 PC, might change later
            config=config,
            debug=False,
        )

        st = Story(
            story_id=story_id,
            title=r['name'],
            setting=r['setting'],
            goal=r['goal'],
            description=form.description.data,
            user_id=current_user.user_id
        )

        db.session.add(st)
        db.session.commit()

        flash('Your story is now live!')
        return redirect(url_for('story.new', story_id=st.story_id))
    return render_template('story/new.html', title='New Story', form=form)
