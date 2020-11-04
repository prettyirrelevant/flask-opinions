from flask_login import UserMixin
from sqlalchemy import func

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id: int):
    return User.query.get(user_id)


followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("users.id")),
)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(155), nullable=False, unique=True)
    full_name = db.Column(db.String(30), nullable=False)
    registered_on = db.Column(db.DateTime, default=func.now(), nullable=False)
    profile_picture = db.Column(db.String(150), default="matthew.png")
    confirmed_on = db.Column(db.DateTime, nullable=True)
    confirmed = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(190), nullable=False)
    followed = db.relationship(
        "User",
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<User (username={self.username} email={self.email})>"

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(155), nullable=False)
    time_to_read = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("posts", order_by=id))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f"<Post (title={self.title}, author={self.user.email}, content={self.content[:10]}...)>"


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post = db.relationship("Post", backref=db.backref("comments", order_by=id))
    user = db.relationship("User", backref=db.backref("user_comments", order_by=id))
    message = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Comment (message={self.message[:10]}..., author={self.user.email}, post_title={self.post.title})>"
