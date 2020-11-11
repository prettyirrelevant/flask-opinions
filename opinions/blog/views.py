import secrets

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from slugify import slugify

from .. import db
from ..models import Comment, Post
from . import blog
from .forms import CommentForm, CreatePost
from .utils import get_time_to_read, save_photo


@blog.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 4, False)
    next_url = url_for("blog.index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("blog.index", page=posts.prev_num) if posts.has_prev else None
    return render_template(
        "blog/index.html",
        title="Opinions - Express Yourself",
        posts=posts.items,
        prev_url=prev_url,
        next_url=next_url,
    )


@blog.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = CreatePost()

    if form.validate_on_submit():
        time_to_read = get_time_to_read(form.content.data)
        post = Post(
            title=form.title.data,
            content=form.content.data,
            time_to_read=time_to_read,
            user_id=current_user.id,
        )
        post.slug = slugify(form.title.data) + "-" + secrets.token_hex(8)

        # TODO catch errors later
        db.session.add(post)
        db.session.commit()

        flash("Your opinion has been uploaded successfully", "success")
        return redirect(
            url_for(
                "blog.view_post", username=current_user.username, post_slug=post.slug
            )
        )

    return render_template("blog/create.html", title="Create | Opinions", form=form)


@blog.route("/<username>/<post_slug>", methods=["POST", "GET"])
def view_post(username, post_slug):
    form = CommentForm()
    post = Post.query.filter_by(slug=post_slug).first()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to be logged in to add a comment", "warning")
            return redirect(url_for("users.login", next=f"/{username}/{post_slug}"))

        # create new comment
        comment = Comment(
            post_id=post.id, user_id=current_user.id, message=form.message.data
        )
        db.session.add(comment)
        db.session.commit()

        flash("Comment added successfully", "success")
        return redirect(
            url_for("blog.view_post", username=username, post_slug=post_slug)
        )

    return render_template(
        "blog/view_post.html", title=f"{post.title} | Opinions", post=post, form=form
    )


@blog.route("/upload_attachment", methods=["POST"])
def upload_attachment():
    file = request.files["file"]
    url = save_photo(file)
    return jsonify({"url": url})
