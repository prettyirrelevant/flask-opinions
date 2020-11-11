import math
import os
import re
import secrets
from html.parser import HTMLParser
from io import StringIO

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from flask import current_app as app


class ParseHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    # convert entities to utf-8
    parser = HTMLParser()
    html = parser.unescape(html)

    s = ParseHTML()
    s.feed(html)
    return s.get_data()


def get_time_to_read(text: str):
    striped_text = strip_tags(text)
    word_cleaned = re.sub(r" /[^\w ]/g", "", striped_text)
    word_count = len(word_cleaned.split(" "))
    reading_time = math.floor(word_count / 200)

    if reading_time <= 1:
        return f"{str(reading_time)} min"
    else:
        return f"{str(reading_time)} mins"


def save_photo(file):
    uploaded_picture = upload(file, folder="opinions")

    url, options = cloudinary_url(uploaded_picture["public_id"], format="jpg")

    return url
