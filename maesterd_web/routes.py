from flask import render_template, flash, redirect, url_for, request
from urllib.parse import urlsplit
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from maesterd_web import app, db
from maesterd_web.forms import LoginForm, RegistrationForm, StoryForm, ChapterForm
from maesterd_web.models import User, Story, Chapter
from maesterd_web.settings import STORIES_PER_PAGE, CHAPTERS_PER_PAGE

from openai import OpenAI, OpenAIError
import requests.exceptions




@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = sa.select(Story).where(Story.user_id==user.user_id).order_by(Story.created_at.desc())
    stories = db.paginate(query, page=page, per_page=STORIES_PER_PAGE, error_out=False)
    next_url = url_for('user_profile', page=stories.next_num) if stories.has_next else None
    prev_url = url_for('user_profile', page=stories.prev_num) if stories.has_prev else None

    return render_template('user.html', user=user,
                           stories=stories.items, next_url=next_url, prev_url=prev_url)


def make_openai_request(prompt, api_key):
    # return 'that is the fake api response'
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to a valid model name
            messages=[
                {"role": "system", "content": "You are a dungeons and dragons role play game master"},
                {"role": "user", "content": prompt}
            ],
            timeout=30  # Add a timeout to prevent hanging
        )
        return completion.choices[0].message.content
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.RequestException("Connection error. Please check your internet connection.")
    except OpenAIError as e:
        raise  # Re-raise OpenAI specific errors to be handled in the route
    except Exception as e:
        raise Exception(f"Unexpected error in OpenAI request: {str(e)}")


@app.route('/story/<int:story_id>', methods=['GET', 'POST'])
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
                chapter.response = make_openai_request(chapter.prompt, form.api_key.data)
            except OpenAIError as openai_error:
                if "invalid_api_key" in str(openai_error).lower():
                    flash('Invalid OpenAI API key. Please check your API key and try again.', 'error')
                elif "rate_limit" in str(openai_error).lower():
                    flash('Rate limit exceeded. Please wait a moment before trying again.', 'error')
                else:
                    flash('OpenAI API error: ' + str(openai_error), 'error')
                return redirect(url_for('story', story_id=story_id))
            except requests.exceptions.RequestException:
                flash('Connection error. Please check your internet connection and try again.', 'error')
                return redirect(url_for('story', story_id=story_id))
            except Exception as e:
                app.logger.error(f"Unexpected error in OpenAI request: {str(e)}")
                flash('An unexpected error occurred. Please try again.', 'error')
                return redirect(url_for('story', story_id=story_id))

            # If we got here, the API request was successful
            db.session.add(chapter)
            db.session.commit()
            flash('New chapter is now live!', 'success')

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error generating chapter: {str(e)}")
            flash('Database error occurred. Please try again.', 'error')

        return redirect(url_for('story', story_id=story_id))

    return render_template('story.html', chapters=chapters, story=story, form=form)

@app.route('/new_story', methods=['GET', 'POST'])
@login_required
def new_story():
    form = StoryForm()
    if form.validate_on_submit():
        story = Story(title=form.title.data, description=form.description.data, user_id=current_user.user_id)
        db.session.add(story)
        db.session.commit()
        flash('Your story is now live!')
        return redirect(url_for('story', story_id=story.story_id))
    return render_template('new_story.html', title='New Story', form=form)