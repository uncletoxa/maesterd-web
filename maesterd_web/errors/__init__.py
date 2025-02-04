from flask import Blueprint

bp = Blueprint('errors', __name__)
from maesterd_web.errors import handlers
