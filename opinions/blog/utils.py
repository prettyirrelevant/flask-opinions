import math
import os
import re
import secrets
from html.parser import HTMLParser
from io import StringIO

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
    random_name = secrets.token_hex(8)
    _, ext = os.path.splitext(file.filename)
    picture_name = random_name + ext

    file.save(os.path.join(app.config["UPLOADED_PHOTOS_DEST"], picture_name))

    return picture_name
