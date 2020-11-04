import jwt
from time import time
from flask import current_app as app

from opinions.models import User

SECRET_KEY = app.config["SECRET_KEY"]


def generate_confirmation_token(email):
    return jwt.encode(
        {"confirm": email, "exp": time() + 3600}, SECRET_KEY, algorithm="HS256"
    ).decode("utf-8")


def confirm_token(token):
    try:
        email = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["confirm"]
    except:
        return False

    return email


def generate_reset_token(user):
    return jwt.encode(
        {"reset_password": user.id, "exp": time() + 600}, SECRET_KEY, algorithm="HS256"
    ).decode("utf-8")


def confirm_reset_token(token):
    try:
        id = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["reset_password"]
    except:
        return False

    return User.query.get(id)
