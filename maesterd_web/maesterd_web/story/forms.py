from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from maesterd_web.settings import MAX_TITLE_LENGTH


class StoryForm(FlaskForm):
    # title = TextAreaField('An optional title to your story!')  # NOTE: story title is now auto generated!
    description = TextAreaField("Please describe your adventure! (optional)")
    submit = SubmitField('Submit')


class ChapterForm(FlaskForm):
    prompt = TextAreaField('What do you do?', validators=[DataRequired()])
    api_key = TextAreaField('OpenAI api key', validators=[DataRequired()])
    submit = SubmitField('Submit')
