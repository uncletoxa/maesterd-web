from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
import sqlalchemy as sa
from maesterd_web import db
from maesterd_web.models import User
from maesterd_web.settings import MAX_TITLE_LENGTH


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


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
