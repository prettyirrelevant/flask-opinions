import os
import secrets

from flask import current_app as app
from PIL import Image


def save_picture(form_picture) -> str:
    random_name = secrets.token_hex(10)
    _, ext = os.path.splitext(form_picture.filename)
    picture_name = random_name + ext

    image: Image.Image = Image.open(form_picture)
    image.thumbnail((600, 600))
    image.save(os.path.join(app.config["UPLOADED_PROFILES_DEST"], picture_name))

    return picture_name
