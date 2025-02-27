from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class StoryForm(FlaskForm):
    description = TextAreaField("Please describe your adventure! (optional)")
    submit = SubmitField('Submit')


class ChapterForm(FlaskForm):
    prompt = TextAreaField('What do you do?', validators=[DataRequired()])
    submit = SubmitField('Submit')
