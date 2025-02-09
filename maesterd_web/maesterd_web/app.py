import logging
import sys

from flask import Flask, render_template
from maesterd_web import public, user, story
from maesterd_web.extensions import db, migrate, login, moment


def create_app():
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/"""
    app = Flask(__name__.split(".")[0], instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=True)
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    return app

def register_extensions(app):
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)


def register_blueprints(app):
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    app.register_blueprint(story.views.blueprint)


def register_error_handlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"errors/{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None

def configure_logger(app):
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
