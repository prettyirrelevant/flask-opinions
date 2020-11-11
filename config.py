import os
from os import environ, path

from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))


class BaseConfig:
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_DEBUG = environ.get("FLASK_DEBUG")
    FLASK_ENV = environ.get("FLASK_DEBUG")


class Config(BaseConfig):
    SECRET_KEY = environ.get("SECRET_KEY") or "!secret"
    SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT") or "salty"

    # Flask-Mail
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = environ.get("APP_MAIL_USERNAME")
    MAIL_PASSWORD = environ.get("APP_MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = environ.get("APP_MAIL_USERNAME")
    MAIL_DEBUG = False

    SQLALCHEMY_DATABASE_URI = (
        environ.get("SQLALCHEMY_DATABASE_URI") or f"sqlite:////{os.getcwd()}/db.sqlite3"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") or False
    )
    CLOUDINARY_URL = environ.get("CLOUDINARY_URL")
