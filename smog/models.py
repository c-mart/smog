from helpers import *
from os import urandom
from datetime import datetime
from smog import db


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    pw_hash = db.Column(db.Binary)
    pw_salt = db.Column(db.Binary)
    active = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, email, name, password):
        # Todo perform validation that this is an email address
        self.email = email
        self.name = name
        self.pw_salt = urandom(16)
        self.pw_hash = pw_hash(password, self.pw_salt)
        self.create_date = datetime.utcnow()

    def __repr__(self):
        return '<User %s>', self.email

    # TODO understand what the @property does
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    permalink = db.Column(db.String, unique=True)
    body = db.Column(db.Text)
    create_date = db.Column(db.DateTime)
    edit_date = db.Column(db.DateTime)
    published = db.Column(db.Boolean)
    comments_allowed = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user_id, description=None, permalink=None, create_date=None,
                 edit_date=None, published=True, comments_allowed=True):
        self.title = title
        self.body = body
        if description == '' or description is None:
            self.description = self.title
        else:
            self.description = description
        if permalink == '' or permalink is None:
            self.permalink = self.title.lower().replace(' ', '-')
        else:
            # TODO perform some permalink validation, e.g. ensure no invalid characters
            self.permalink = permalink
        if create_date is None:
            self.create_date = datetime.utcnow()
        else:
            # TODO ensure create_date is in the right format if passed
            self.create_date = create_date
        if edit_date is None:
            self.edit_date = datetime.utcnow()
        else:
            # TODO ensure edit_date is in the right format if passed
            self.edit_date = edit_date
        self.published = published
        self.comments_allowed = comments_allowed
        self.user_id = user_id

    def __repr__(self):
        return '<Post %s>' % self.title

    def user_name(self):
        return User.query.filter_by(id=self.user_id).one().name