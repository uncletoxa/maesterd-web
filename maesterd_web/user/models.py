import sqlalchemy as sa
import sqlalchemy.orm as so

from hashlib import md5
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from maesterd_web import db, login
from maesterd_web.models import Story, UserKey


class User(UserMixin, db.Model):
    user_id: so.Mapped[int] = so.mapped_column(sa.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64),unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True)
    password_hash: so.Mapped[str | None] = so.mapped_column(sa.String(256))
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))

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
