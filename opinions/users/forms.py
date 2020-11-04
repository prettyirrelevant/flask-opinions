from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    Length,
    DataRequired,
    Email,
    ValidationError,
    Regexp,
    EqualTo,
)

from ..models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Regexp(
                "^(?=[a-zA-Z0-9._]{3,20}$)(?!.*[_.]{2})[^_.].*[^_.]$",
                message="Invalid format",
            ),
        ],
        description="Only alphanumeric characters, hyphen and dot are allowed",
    )
    full_name = StringField(
        "Full Name", validators=[Length(min=2, max=150), DataRequired()]
    )
    email = StringField("Email Address", validators=[Email(), DataRequired()])
    password = PasswordField(
        "Password",
        validators=[Length(min=8, max=30), DataRequired()],
        description="Password should contain at least 8 characters",
    )

    def validate_email(form, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email address already attached to an existing user.")

    def validate_username(form, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already attached to an existing user.")


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[Email()])
    password = PasswordField(
        "Password",
        validators=[Length(min=8, max=30), DataRequired()],
        description="Password should contain at least 8 characters",
    )
    remember_me = BooleanField("Remember Me")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])

    def validate_email(form, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Email address does not exists.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=30)],
        description="Password should contain at least 8 characters",
    )
    password2 = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password"), Length(min=8, max=30)],
        description="Password must match",
    )


class EditProfileForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    full_name = StringField(
        "Full Name", validators=[Length(min=2, max=150), DataRequired()]
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Regexp(
                "^(?=[a-zA-Z0-9._]{3,20}$)(?!.*[_.]{2})[^_.].*[^_.]$",
                message="Invalid format",
            ),
        ],
        description="Only alphanumeric characters, hyphen and dot are allowed",
    )
    profile_picture = FileField(
        "Profile Picture", validators=[FileAllowed(["jpg", "png", "jpeg", "svg"])]
    )

    def validate_email(form, email):
        if not current_user.email == email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "Email address already attached to an existing user."
                )


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")
