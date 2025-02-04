from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
import sqlalchemy as sa
from maesterd_web import db
from maesterd_web.models import User
from maesterd_web.settings import MAX_TITLE_LENGTH


c


class StoryForm(FlaskForm):
    title = TextAreaField('The title of your story',
                          validators=[DataRequired(), Length(min=1, max=MAX_TITLE_LENGTH)])
    description = TextAreaField('An optional description')
    submit = SubmitField('Submit')

class ChapterForm(FlaskForm):
    prompt = TextAreaField('Write your prompt',
                          validators=[DataRequired()])
    api_key = TextAreaField('OpenAI api key',
                          validators=[DataRequired()])
    submit = SubmitField('Submit')
