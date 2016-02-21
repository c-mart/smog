from smog import app, limiter, login_manager
import flask_login
from smog.models import *
from smog.helpers import *
from flask import redirect, url_for, request, session, flash, render_template, make_response
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound


# TODO write some docstrings
@login_manager.user_loader
def user_loader(user_id):
    try:
        return User.query.filter_by(id=int(user_id)).one()
    except NoResultFound():
        return None


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("6/minute", methods=['POST'])
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
        if len(posts) == 0:
            flash('No posts yet.')
    else:
        # Template expects a list of posts, so we return a list even though it's just one post
        posts = [Post.query.filter_by(permalink=permalink, published=True).first_or_404()]
    return render_template('posts.html', posts=posts)


@app.route('/unpublished')
@flask_login.login_required
def view_unpublished():
    posts = Post.query.filter_by(published=False).order_by(Post.create_date.desc()).all()
    return render_template('posts.html', posts=posts, unpublished=True)


@app.route('/create', methods=['GET', 'POST'])
@flask_login.login_required
def create_edit_post():
    if request.method == 'POST':
        if request.form.get('update_id'):
            # Updating existing post in database
            post = Post.query.filter_by(id=request.form['update_id']).first_or_404()
            post.title = request.form['title']
            post.body = request.form['body']
            post.description = request.form['description']
            post.permalink = request.form['permalink']
            post.published = True if 'published' in request.form else False
            post.comments_allowed = True if 'comments_allowed' in request.form else False
            post.edit_date = datetime.utcnow()
            post.user_id = session['user_id']
        else:
            # Creating new post in database
            post = Post(title=request.form['title'],
                        body=request.form['body'],
                        description=request.form['description'],
                        permalink=request.form['permalink'],
                        published=True if 'published' in request.form else False,
                        comments_allowed=True if 'comments_allowed' in request.form else False,
                        user_id=session['user_id']
                        )
        try:
            db.session.add(post)
            db.session.commit()
        except (IntegrityError, InvalidRequestError):
            db.session.rollback()
            flash('There was a problem creating your post. Please make sure that another post does not already have '
                  'your desired post title and permalink.')
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


@app.errorhandler(429)
def rate_limit_exceeded_handler(e):
    print(e)
    flash('You have tried doing that too often. Please wait a minute before trying again.')
    # Return statement should be generalized if we ever use rate limiting for actions other than logging in
    return make_response(redirect(url_for('login')))

# Jinja2 display filters


@app.template_filter('date_format')
def date_format(value, formatstr='%Y-%m-%d'):
    return value.strftime(formatstr)