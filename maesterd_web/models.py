from hashlib import md5
from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from maesterd_web import app, db, migrate, login
from maesterd_web.settings import MAX_TITLE_LENGTH
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from roman import toRoman





class Story(db.Model):
    story_id: so.Mapped[int] = so.mapped_column(sa.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(MAX_TITLE_LENGTH))
    description: so.Mapped[str] = so.mapped_column(sa.String(), nullable=True)
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
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
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    story_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Story.story_id), index=True)

    part_of_story: so.Mapped['Story'] = so.relationship(back_populates='chapters')

    def __repr__(self):
        return f'<Chapter {toRoman(self.chapter_number)}>'


class UserKey(db.Model):
    user_key_id: so.Mapped[int] = so.mapped_column(sa.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.user_id), index=True)

    user_key_owner_id: so.Mapped['User'] = so.relationship(back_populates='user_key')