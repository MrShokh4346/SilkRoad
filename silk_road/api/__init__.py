from flask import Blueprint

bp = Blueprint("api",  __name__)

from silk_road.api import views
