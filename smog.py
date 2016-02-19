from datetime import datetime
from flask import Flask, redirect, url_for, request, session, abort, flash, render_template
import flask.ext.login as flask_login
from flask_sqlalchemy import SQLAlchemy
from flask.ext.misaka import Misaka
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from hashlib import pbkdf2_hmac
from os import urandom, path

# Configuration
DB_PATH = '/tmp/smog.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH
SECRET_KEY = 'CHANGEME123'
USERNAME = 'admin'
PASSWORD = 'changeme123'
DEBUG = True

# Initializing application and extensions
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
Misaka(app)


# Helper functions for login and authentication
@login_manager.user_loader
def user_loader(user_id):
    try:
        return User.query.filter_by(id=int(user_id)).one()
    except NoResultFound():
        return None


def pw_hash(password, salt):
    return pbkdf2_hmac('sha512', password, salt, 100000)


# Models
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String)
    name = db.Column(db.String)
    pw_hash = db.Column(db.Binary)
    pw_salt = db.Column(db.Binary)
    active = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime)

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

    def __init__(self, title, body, description=None, permalink=None, create_date=None,
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

    def __repr__(self):
        return '<Post %s>' % self.title


# Create database if it's not there
if __name__ == '__main__':
    if not path.exists(DB_PATH):
        db.create_all()
        testuser = User('test@test.com', 'Test User', 'changeme123')
        db.session.add(testuser)
        db.session.commit()


# Views
# TODO write some docstrings
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).one()
        except NoResultFound:
            pass  # User doesn't exist, skip to invalid block
        else:
            if user.pw_hash == pw_hash(request.form['password'], user.pw_salt) and user.active is True:
                flask_login.login_user(user)
                flash('You are logged in.')
                # TODO fix this. Args need to be passed from login form.
                '''
                # If we ever implement multiple user access levels then we need to check if user can access 'next'
                next_page = request.args.get('next')
                print(next_page)
                '''
                return redirect(url_for('view_posts'))

        flash('Invalid email or password, try again.')
        return render_template('login.html')

login_manager.login_view = 'login'


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash('You are logged out.')
    return redirect(url_for('view_posts'))


# TODO also allow short post URLs with post ID
@app.route('/')
@app.route('/posts/')
@app.route('/posts/<permalink>')
def view_posts(permalink=None):
    if permalink is None:
        posts = Post.query.filter_by(published=True).order_by(Post.create_date.desc()).all()
    else:
        posts = Post.query.filter_by(permalink=permalink, published=True).first_or_404()
    return render_template('posts.html', posts=posts)


@app.route('/unpublished')
@flask_login.login_required
def view_unpublished():
    posts = Post.query.filter_by(published=False).order_by(Post.create_date.desc()).all()
    return render_template('posts.html', posts=posts, unpublished=True)


@app.route('/create', methods=['GET', 'POST'])
@flask_login.login_required
def create_edit_post():
    # TODO fix this
    # if not session.get('logged_in'):
    #     abort(401)
    if request.method == 'POST':
        if request.form['update_id']:
            # Updating existing post in database
            post = Post.query.filter_by(id=request.form['update_id']).first_or_404()
            post.title = request.form['title']
            post.body = request.form['body']
            post.description = request.form['description']
            post.permalink = request.form['permalink']
            post.published = True if 'published' in request.form else False
            post.comments_allowed = True if 'comments_allowed' in request.form else False
            post.edit_date = datetime.utcnow()
        else:
            # Creating new post in database
            post = Post(title=request.form['title'],
                        body=request.form['body'],
                        description=request.form['description'],
                        permalink=request.form['permalink'],
                        published=True if 'published' in request.form else False,
                        comments_allowed=True if 'comments_allowed' in request.form else False,
                        )
        # todo add error checking e.g. if model doesn't like input from view
        try:
            db.session.add(post)
            db.session.commit()
        except (IntegrityError, InvalidRequestError):
            db.session.rollback()
            flash('There was a problem creating your post. \
                Please make sure that another post does not already have your desired post title and permalink.')
            return render_template('create_edit.html', formdata=request.form)
        else:
            flash('Post successful')
            return redirect(url_for('view_posts'))
    elif request.method == 'GET' and request.args.get('id') is not None:
        # Editing existing post
        post = Post.query.filter_by(id=request.args.get('id')).first_or_404()
        return render_template('create_edit.html', formdata=post, edit=True)
    elif request.method == 'GET':
        # Composing new post
        return render_template('create_edit.html', formdata=dict())


@app.route('/delete/<post_id>')
@flask_login.login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted.')
    return redirect(url_for('view_posts'))


# Jinja2 display filters


@app.template_filter('date_format')
def date_format(value, formatstr='%Y-%m-%d'):
    return value.strftime(formatstr)

if __name__ == '__main__':
    app.run()