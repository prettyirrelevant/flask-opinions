from flask import current_app as app
from flask import send_from_directory


@app.route("/profiles/<filename>")
def serve_profile(filename):
    return send_from_directory(app.config["UPLOADED_PROFILES_DEST"], filename)


@app.route("/photos/<filename>")
def serve_photo(filename):
    return send_from_directory(app.config["UPLOADED_PHOTOS_DEST"], filename)


@app.route("/thumbnails/<filename>")
def serve_thumbnail(filename):
    return send_from_directory(app.config["UPLOADED_THUMBNAILS_DEST"], filename)
