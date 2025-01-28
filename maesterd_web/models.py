from hashlib import md5
from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from maesterd_web import app, db, migrate, login
from maesterd_web.settings import MAX_TITLE_LENGTH
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from roman import toRoman


class User(UserMixin, db.Model):
    user_id: so.Mapped[int] = so.mapped_column(sa.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True)
    password_hash: so.Mapped[str | None] = so.mapped_column(sa.String(256))

    stories: so.WriteOnlyMapped['Story'] = so.relationship(back_populates='story_author_id')
    user_key: so.WriteOnlyMapped['UserKey'] = so.relationship(back_populates='user_key_owner_id')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.user_id

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=monsterid&s={size}'

@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Story(db.Model):
    story_id: so.Mapped[int] = so.mapped_column(sa.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(MAX_TITLE_LENGTH))
    description: so.Mapped[str] = so.mapped_column(sa.String(), nullable=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.user_id), index=True)

    story_author_id: so.Mapped['User'] = so.relationship(back_populates='stories')
    chapters: so.WriteOnlyMapped['Chapter'] = so.relationship(back_populates='part_of_story')

    def __repr__(self):
        return f'<{self.title}>'


class Chapter(db.Model):
    chapter_id: so.Mapped[int] = so.mapped_column(sa.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    prompt: so.Mapped[str] = so.mapped_column(sa.String())
    response: so.Mapped[str] = so.mapped_column(sa.String())
    chapter_number: so.Mapped[int] = so.mapped_column()
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    story_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Story.story_id), index=True)

    part_of_story: so.Mapped['Story'] = so.relationship(back_populates='chapters')

    def __repr__(self):
        return f'<Chapter {toRoman(self.chapter_number)}>'


class UserKey(db.Model):
    user_key_id: so.Mapped[int] = so.mapped_column(sa.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.user_id), index=True)

    user_key_owner_id: so.Mapped['User'] = so.relationship(back_populates='user_key')