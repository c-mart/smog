from datetime import time
from flask import Flask, redirect, url_for, request, session, abort, flash
from flask_sqlalchemy import SQLAlchemy
import re

# Configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/smog.sqlite'
USERNAME = 'admin'
PASSWORD = 'changeme123'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)


# Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True)
    description = db.Column(db.String())
    permalink = db.Column(db.String())
    body = db.Column(db.Text())
    create_date = db.Column(db.DateTime)
    edit_date = db.Column(db.DateTime)
    published = db.Column(db.Boolean)
    comments_allowed = db.Column(db.Boolean)

    def __init__(self, title, body, description=None, permalink=None, create_date=None,
                 edit_date=None, published=True, comments_allowed=True):
        self.title = title
        self.body = body
        if description is None:
            self.description = ""
        else:
            self.description = description
        if permalink is None:
            self.permalink = title.lower().replace(' ', '-')
        else:
            # TODO perform some permalink validation, e.g. ensure no invalid characters
            self.permalink = permalink
        if create_date is None:
            self.create_date = time.utcnow()
        else:
            # TODO ensure create_date is in the right format
            self.create_date = create_date
        if edit_date is None:
            self.edit_date = time.utcnow()
        else:
            # TODO ensure edit_date is in the right format
            self.edit_date = edit_date
        self.published = published
        self.comments_allowed = comments_allowed

    def __repr__(self):
        return '<Post %s>' % self.title

# Views


@app.route('/')
@app.route('/posts/')
def view_new_posts():
    # TODO fix this
    posts = Post.query.all().__dict__
    return 'Placeholder for viewing new posts'

# TODO also allow short post URLs with post ID
@app.route('/posts/<permalink>')
def view_post(permalink):
    return 'Placeholder for viewing a single post'


@app.route('/create', methods=['GET', 'POST'])
def create_edit_post():
    if not session.get('logged_in'):
        abort(401)
    post = Post(title=request.form['title'],
                body=request.form['body'],
                description=request.form['description'],
                permalink=request.form['permalink'],
                create_date=request.form['create_date'],
                edit_date=request.form['edit_date'],
                published=request.form['published'],
                comments_allowed=request.form['comments_allowed'],
                )
    db.session.add(post)
    db.session.commit()
    flash('New post has been created')
    return redirect(url_for('view_new_posts'))


@app.route('/delete')
def delete_post():
    return 'Placeholder for deleting a post'


@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'Placeholder for logging in'


@app.route('/logout')
def logout():
    return 'Placeholder for logging out'

if __name__ == '__main__':
    app.run()
