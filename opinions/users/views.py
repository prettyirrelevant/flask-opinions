import datetime
import os

from flask import abort
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from .. import bcrypt, db
from ..models import User
from . import users
from .forms import (
    EditProfileForm,
    EmptyForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from .mail import send_email
from .token import (
    confirm_reset_token,
    confirm_token,
    generate_confirmation_token,
    generate_reset_token,
)
from .utils import save_picture


@users.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.profile", username=current_user.username))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            email=form.email.data,
        )
        user.password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        try:
            db.session.add(user)
            db.session.commit()
        except:
            flash("Unable to create account at the moment", "warning")

        token = generate_confirmation_token(user.email)
        confirm_url = url_for("users.confirm_email", token=token, _external=True)
        html = render_template(
            "users/activate.html", confirm_url=confirm_url, user=user.full_name
        )
        subject = "[Opinions] Please confirm your email"
        send_email(user.email, subject, html)

        flash(
            "Account created successfully. A confirmation email has been sent via email.",
            "success",
        )
        return redirect(url_for("users.login"))

    return render_template(
        "users/register.html", form=form, title="Register | Opinions"
    )


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.profile", username=current_user.username))

    form = LoginForm()
    # TODO redirect for @login_required
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
        except:
            flash(
                "We are having issues processing this request at the moment", "warning"
            )
        else:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, form.remember_me.data)

                flash("Logged in successfully", "success")
                next_page = request.args.get("next")
                if not next_page or url_parse(next_page).netloc != "":
                    next_page = url_for("blog.index")
                return redirect(next_page)

            flash("Username and/or password incorrect", "danger")
    return render_template("users/login.html", title="Login | Opinions", form=form)


@users.route("/resend_token")
@login_required
def resend_token():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for("users.confirm_email", token=token, _external=True)
    html = render_template(
        "users/resend.html", confirm_url=confirm_url, user=current_user.full_name
    )
    subject = "Please confirm your email"
    try:
        send_email(current_user.email, subject, html)
    except:
        flash("Unable to send confirmation email at this moment", "danger")
        return redirect(request.referrer)

    flash("Confirmation email sent sucessfully!", "success")
    return redirect(request.referrer)


@users.route("/confirm_account/<token>")
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("users.register"))

    user = User.query.filter_by(email=email).first()

    if user.confirmed:
        flash("Account already confirmed. Please login.", "success")
    else:
        user.confirmed = True

        # checks if the account has previously been confirmed
        if not user.confirmed_on:
            user.confirmed_on = datetime.datetime.now()
        try:
            db.session.commit()
        except:
            flash("Unable to confirm account at the moment!", "warning")

        flash("You have confirmed your account. Thanks!", "success")
    return redirect(url_for("users.profile", username=user.username))


@users.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("users.profile", username=current_user.username))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            if user.confirmed:
                token = generate_reset_token(user)
                reset_url = url_for("users.reset_password", token=token, _external=True)
                html = render_template(
                    "users/reset_password_mail.html",
                    reset_url=reset_url,
                    user=user.full_name,
                )
                subject = "[Opinions] Reset Your Password"
                try:
                    send_email(user.email, subject, html)
                except:
                    flash("Unable to send password reset link at this moment", "danger")
                    return redirect(request.referrer)
                else:
                    flash("Check your email for password reset link", "success")
                    return redirect(url_for("users.login"))

            flash(
                "Sorry, your email was not verified so we cannot send a reset link",
                "danger",
            )
            return redirect(url_for("users.reset_password_request"))

        flash("Something went wrong, try again later", "warning")
    return render_template(
        "users/password_reset_request.html",
        title="Reset Password | Opinions",
        form=form,
    )


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("users.profile", username=current_user.username))
    try:
        user = confirm_reset_token(token)
    except:
        flash("Something went wrong, try again later", "warning")
        return redirect(url_for("blog.index"))

    if not user:
        return redirect(url_for("blog.index"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data)

        # TODO catch the errors in future
        db.session.commit()

        flash("Your password has been reset.")
        return redirect(url_for("users.login"))

    return render_template("users/reset_password.html", form=form)


@users.route("/<username>")
def profile(username):
    form = EmptyForm()
    user = User.query.filter_by(username=username).first()

    if not user:
        abort(404)

    return render_template(
        "users/profile.html", title=f"{user.username} | Opinions", user=user, form=form
    )


@users.route("/edit_profile", methods=["POST", "GET"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # based on say python no dey allow declarations
        previous_img = None
        if form.profile_picture.data:
            picture_name = save_picture(form.profile_picture.data)
            previous_img = current_user.profile_picture
            current_user.profile_picture = picture_name

        if form.email.data != current_user.email:
            current_user.email = form.email.data
            current_user.confirmed = False

        current_user.full_name = form.full_name.data
        db.session.commit()

        # Figuring out how to delete previous profile pictures
        # using cloudinary

        flash("Profile updated successfully!", "success")
        return redirect(url_for("users.profile", username=current_user.username))

    form.email.data = current_user.email
    form.full_name.data = current_user.full_name
    form.username.data = current_user.username
    return render_template(
        "users/edit_profile.html", form=form, title="Edit Profile - Opinions"
    )


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("User {} not found.".format(username), "error")
            return redirect(url_for("blog.index"))

        if user == current_user:
            flash("You cannot follow yourself!", "warning")
            return redirect(url_for("users.profile", username=username))

        current_user.follow(user)
        db.session.commit()

        flash("You are now following {}!".format(username), "success")
        return redirect(url_for("users.profile", username=username))
    else:
        return redirect(url_for("blog.index"))


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("User {} not found.".format(username))
            return redirect(url_for("blog.index"))
        if user == current_user:
            flash("You cannot unfollow yourself!", "warning")
            return redirect(url_for("users.profile", username=username))

        current_user.unfollow(user)
        db.session.commit()

        flash("You are no longer following {}.".format(username), "success")
        return redirect(url_for("users.profile", username=username))
    else:
        return redirect(url_for("blog.index"))


@users.route("/logout")
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for("blog.index"))
