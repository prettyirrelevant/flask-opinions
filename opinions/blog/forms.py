from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length


class CreatePost(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = HiddenField("content", validators=[InputRequired()])


class CommentForm(FlaskForm):
    message = TextAreaField(
        "Message",
        validators=[InputRequired(), Length(min=1, max=150)],
        description="Comment should not exceed 150 characters",
    )
