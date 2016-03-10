import helpers
from os import urandom
from datetime import datetime
from smog import db
from slugify import slugify
from string import replace


class SiteSettings(db.Model):
    """Global site settings. This table only has one row."""

    id = db.Column(db.Integer(), primary_key=True)
    site_title = db.Column(db.String)
    footer_line = db.Column(db.String)
    analytics_code = db.Column(db.String)

    def __init__(self,
                 site_title='smog: Simple Markdown blOG',
                 footer_line='Copyright $year$ Bloggy McAuthorson, all rights reserved.',
                 analytics_code='<!-- Insert analytics code here -->'):
        self.id = 0
        self.site_title = site_title
        self.footer_line = footer_line
        self.analytics_code = analytics_code

    def __repr__(self):
        return '<Site settings>'

    def get_footer_line(self):
        """Returns site footer line, replacing instances of $year$ with current year."""
        return replace(self.footer_line, '$year$', str(datetime.today().year))


class User(db.Model):
    """User object."""

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    pw_hash = db.Column(db.Binary)
    pw_salt = db.Column(db.Binary)
    active = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, email, name, password, active=True):
        # Todo perform validation that this is an email address
        self.email = email
        self.name = name
        self.pw_salt = urandom(16)
        self.pw_hash = helpers.pw_hash(password, self.pw_salt)
        self.create_date = datetime.utcnow()
        self.active = active

    def __repr__(self):
        return '<User %s>', self.email

    # TODO understand what the @property does
    @property
    def is_authenticated(self):
        """Flask-login requires this for some reason"""
        return True

    @property
    def is_active(self):
        """Returns boolean indicating whether user is active (i.e. they can log in)."""
        return self.active

    @property
    def is_anonymous(self):
        """Flask-login requires this for some reason"""
        return False

    def get_id(self):
        """Flask-login requires this for some reason"""
        return unicode(self.id)


class Post(db.Model):
    """Post object."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    permalink = db.Column(db.String, unique=True)
    body = db.Column(db.Text)
    create_date = db.Column(db.DateTime)
    edit_date = db.Column(db.DateTime)
    static_page = db.Column(db.Boolean)
    static_page_in_timeline = db.Column(db.Boolean)
    static_page_link_title = db.Column(db.String)
    published = db.Column(db.Boolean)
    comments_allowed = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __init__(self,
                 title,
                 body,
                 user_id,
                 description=None,
                 permalink=None,
                 create_date=None,
                 edit_date=None,
                 static_page=False,
                 static_page_in_timeline=False,
                 static_page_link_title=None,
                 published=True,
                 comments_allowed=True):
        self.title = title
        self.body = body
        self.user_id = user_id
        if description == '' or description is None:
            self.description = self.title
        else:
            self.description = description

        # Cleaning up permalink with slugify
        if permalink == '' or permalink is None:
            # Generate permalink from title if user doesn't specify a permalink
            self.permalink = slugify(self.title)
        else:
            self.permalink = slugify(permalink)

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
        self.static_page = static_page
        self.static_page_in_timeline = static_page_in_timeline

        if static_page_link_title == '' or static_page_link_title is None:
            # Auto-generate static page link title if user doesn't provide it
            self.static_page_link_title = title
        else:
            self.static_page_link_title = static_page_link_title

    def __repr__(self):
        return '<Post %s>' % self.title

    def user_name(self):
        """Retrieves user name associated with a post."""
        return User.query.filter_by(id=self.user_id).one().name


class Comment(db.Model):
    """Post comment object."""

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    author_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    guest_author_name = db.Column(db.String)
    guest_author_email = db.Column(db.String)
    body = db.Column(db.Text)
    create_date_time = db.Column(db.DateTime)

    def __init__(self,
                 post_id,
                 body,
                 author_user_id=None,
                 guest_author_name=None,
                 guest_author_email=None):
        self.post_id = post_id
        if author_user_id:  # Logged-in commenter
            self.author_user_id = author_user_id
        else:  # Guest commenter
            if all([guest_author_name, guest_author_email]):
                self.guest_author_name = guest_author_name
                self.guest_author_email = guest_author_email
            else:
                raise Exception('New comment requires either a logged-in user ID or a guest author name and email')
        if guest_author_name is not None:
            self.guest_author_name = guest_author_name
            self.guest_author_email = guest_author_email
        self.body = body
        self.create_date_time = datetime.utcnow()

    def __repr__(self):
        return '<Comment %s>' % self.body

    def user_name(self):
        """Retrieves user name associated with a comment."""
        return User.query.filter_by(id=self.author_user_id).one().name
