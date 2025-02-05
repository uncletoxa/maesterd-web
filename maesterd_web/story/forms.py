from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from maesterd_web.settings import MAX_TITLE_LENGTH


class StoryForm(FlaskForm):
    title = TextAreaField('The title of your story',
                          validators=[DataRequired(), Length(min=1, max=MAX_TITLE_LENGTH)])
    description = TextAreaField('An optional description')
    submit = SubmitField('Submit')


class ChapterForm(FlaskForm):
    prompt = TextAreaField('Write your prompt', validators=[DataRequired()])
    api_key = TextAreaField('OpenAI api key', validators=[DataRequired()])
    submit = SubmitField('Submit')
