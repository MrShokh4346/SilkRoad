from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager

UPLOAD_FOLDER = 'static/photos/'


naming_convention = {
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


    db.init_app(app=app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from silk_road.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth/v1")
    
    from silk_road.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    from silk_road import models
    with app.app_context():
        db.create_all()

    return app