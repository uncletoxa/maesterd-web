from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

__all__ = ['login', 'db', 'migrate']

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
