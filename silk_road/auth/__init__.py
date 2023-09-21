from flask import Blueprint

bp = Blueprint("auth",  __name__)

from silk_road.auth import views
