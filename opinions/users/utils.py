import os
import secrets

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from flask import current_app as app


def save_picture(form_picture) -> str:
    uploaded_picture = upload(form_picture, folder="opinions")

    url, options = cloudinary_url(
        uploaded_picture["public_id"], format="jpg", crop="fill", width=600, height=600
    )

    return url
