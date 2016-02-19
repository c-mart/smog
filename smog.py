from datetime import datetime
from flask import Flask, redirect, url_for, request, session, abort, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from flask.ext.misaka import Misaka
from sqlalchemy.exc import IntegrityError
import os

# Configuration
DB_PATH = '/tmp/smog.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH
SECRET_KEY = 'CHANGEME123'
USERNAME = 'admin'
PASSWORD = 'changeme123'
DEBUG = True

# Initializing application
app = Flask(__name__)
app.config.from_object(__name__)
Misaka(app)
db = SQLAlchemy(app)


# Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True)
    description = db.Column(db.String())
    permalink = db.Column(db.String(), unique=True)
    body = db.Column(db.Text())
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
            # TODO ensure create_date is in the right format
            self.create_date = create_date
        if edit_date is None:
            self.edit_date = datetime.utcnow()
        else:
            # TODO ensure edit_date is in the right format
            self.edit_date = edit_date
        self.published = published
        self.comments_allowed = comments_allowed

    def __repr__(self):
        return '<Post %s>' % self.title

# Initialize database
if not os.path.exists(DB_PATH):
    db.create_all()


# Views
# TODO also allow short post URLs with post ID
@app.route('/')
@app.route('/posts/')
@app.route('/posts/<permalink>')
def view_posts(permalink=None):
    if permalink is None:
        if request.args.get('published') == 'false':
            # Get unpublished posts
            posts = Post.query.filter_by(published=False).order_by(Post.create_date.desc()).all()
        else:
            # Get only published posts
            posts = Post.query.filter_by(published=True).order_by(Post.create_date.desc()).all()
    else:
        posts = Post.query.filter_by(permalink=permalink, published=True).first_or_404()
    return render_template('posts.html', posts=posts)


@app.route('/create', methods=['GET', 'POST'])
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
        except IntegrityError:
            flash('There was a problem creating your post. \
                Please make sure that your post title and permalink are unique.')
            return render_template('create_edit.html', formdata=request.form)
        else:
            flash('Post created successfully')
            return redirect(url_for('view_posts'))
    elif request.method == 'GET' and request.args.get('id') is not None:
        # Editing existing post
        post = Post.query.filter_by(id=request.args.get('id')).first_or_404()
        return render_template('create_edit.html', formdata=post, edit=True)
    elif request.method == 'GET':
        # Composing new post
        return render_template('create_edit.html', formdata=dict())


@app.route('/delete')
def delete_post():
    return 'Placeholder for deleting a post'


@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'Placeholder for logging in'


@app.route('/logout')
def logout():
    return 'Placeholder for logging out'

# Jinja2 display filters


@app.template_filter('date_format')
def date_format(value, formatstr='%Y-%m-%d'):
    return value.strftime(formatstr)

if __name__ == '__main__':
    app.run()
