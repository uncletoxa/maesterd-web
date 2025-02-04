import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from flask_login import LoginManager
from flask_moment import Moment

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py', silent=True)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
moment = Moment(app)
login.login_view = 'login'

from maesterd_web import routes, models, errors


if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/maesterd-web.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Maesterd-web startup')


# def configure_extensions(app):
#     db.init_app(app)
#     login.init_app(app)
#     migrate.init_app(app, db)
#
#
# def create_app():
#     app = Flask(__name__, instance_relative_config=True)
#     app.config.from_pyfile('config.py', silent=True)  # load config that is not version controlled
#
#     configure_extensions(app)
#
#     # from . import story
#     # maesterd_web.register_blueprint(blog.bp)
#     # maesterd_web.add_url_rule('/', endpoint='index')
#     #
#     # maesterd_web.register_blueprint(user.bp)
#
#     return app
