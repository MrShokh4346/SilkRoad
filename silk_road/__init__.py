from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager
from dotenv.main import load_dotenv
from flask_mail import Mail
import os

load_dotenv()


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
mail = Mail()



def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
    app.config["SECRET_KEY"] = os.environ['SECRET_KEY']
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'silkrouteitc21@gmail.com'
    app.config['MAIL_PASSWORD'] = os.environ['GMAIL_PASSWORD']
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True


    db.init_app(app=app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    from silk_road.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth/v1")
    
    from silk_road.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    from silk_road import models
    with app.app_context():
        db.create_all()

    return app