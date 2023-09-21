from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["JWT_SECRET_KEY"] = "super-secret"

    db.init_app(app=app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from silk_road.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth/v1")

    from silk_road import models
    with app.app_context():
        db.create_all()

    return app