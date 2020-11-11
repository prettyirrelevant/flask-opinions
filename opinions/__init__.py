import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
cors = CORS()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

login_manager.login_view = "users.login"
login_manager.login_message = "You need to be logged in to access this page."
login_manager.login_message_category = "warning"


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        from .blog import blog
        from .users import users

        app.register_blueprint(users)
        app.register_blueprint(blog)

        if not app.debug and not app.testing:

            if app.config["LOG_TO_STDOUT"]:
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            else:
                if not os.path.exists("logs"):
                    os.mkdir("logs")
                file_handler = RotatingFileHandler(
                    "logs/opinions.log", maxBytes=10240, backupCount=10
                )
                file_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s %(levelname)s: %(message)s "
                        "[in %(pathname)s:%(lineno)d]"
                    )
                )
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Application has started")

        return app
