from smog import app, limiter, login_manager
import flask_login
import smog.models as models
import smog.forms as forms
import smog.helpers
from flask import abort, redirect, url_for, request, session, flash, render_template, make_response, g
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from slugify import slugify
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
from mistune import markdown
from functools import wraps


@login_manager.user_loader
def user_loader(user_id):
    """Retrieves user object for login manager."""
    try:
        return models.User.query.filter_by(id=int(user_id)).one()
    except NoResultFound():
        return None


def get_static_stuff(f):
    """Decorator to retrieve static pages and site settings, storing them in `g` for display in templates"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        static_pages = models.Post.query.filter_by(published=True, static_page=True).all()
        g.static_pages = static_pages
        settings = models.SiteSettings.query.filter_by(id=0).one()
        g.site_settings = settings
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("6/minute", methods=['POST'])
@get_static_stuff
def login():
    """Display login page or process login attempt"""
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        try:
            user = models.User.query.filter_by(email=request.form['email']).one()
        except NoResultFound:
            # TODO refactor this logic block to DRY later
            flash('No active account associated with that email and password, try again.')
            return render_template('login.html')
        else:
            if user.pw_hash == smog.helpers.pw_hash(request.form['password'], user.pw_salt) and user.active is True:
                flask_login.login_user(user)
                flash('You are logged in.')
                # TODO fix this. Args need to be passed from login form.
                '''
                # If we ever implement multiple user access levels then we need to check if user can access 'next'
                next_page = request.args.get('next')
                print(next_page)
                '''
                return redirect(url_for('view_posts'))
            else:
                # TODO refactor this logic block to DRY earlier
                flash('No active account associated with that email and password, try again.')
                return render_template('login.html')

login_manager.login_view = 'login'


@app.route('/logout')
@flask_login.login_required
def logout():
    """Log user out"""
    flask_login.logout_user()
    flash('You are logged out.')
    return redirect(url_for('view_posts'))


@app.route('/site-settings', methods=['GET', 'POST'])
@flask_login.login_required
@get_static_stuff
def site_settings():
    """Allow user to edit global site settings"""
    settings = models.SiteSettings.query.filter_by(id=0).one()
    if request.method == 'POST':
        settings.site_title = request.form['site_title']
        settings.footer_line = request.form['footer_line']
        settings.analytics_code = request.form['analytics_code']
        models.db.session.add(settings)
        models.db.session.commit()
        flash('Site settings have been updated.')
        return redirect(url_for('site_settings'))
    elif request.method == 'GET':
        return render_template('site_settings.html', formdata=settings)


@app.route('/manage-users', methods=['GET', 'POST'])
@flask_login.login_required
@get_static_stuff
def manage_users():
    """Allow user to CRUD user accounts"""
    users = models.User.query.all()
    return render_template('manage_users.html', users=users)


@app.route('/create-edit-user', methods=['GET', 'POST'])
@flask_login.login_required
@get_static_stuff
def create_edit_user():
    if request.method == 'POST':
        if request.form.get('update_id'):
            # Update user account
            if request.form['update_id'] == session['user_id'] and request.form.get('active') == "False":
                flash('Error: you cannot disable your own user account.')
                return redirect(url_for('manage_users'))
            user = models.User.query.filter_by(id=request.form['update_id']).first_or_404()
            user.name = request.form['name']
            user.email = request.form['email']
            user.active = True if request.form.get('active') == "True" else False
            if request.form['password']:
                user.pw_hash = models.helpers.pw_hash(request.form['password'], user.pw_salt)
        else:
            # Create new user account
            user = models.User(name=request.form['name'],
                               email=request.form['email'],
                               password=request.form['password'],
                               active=True if request.form['active'] == "True" else False)
        models.db.session.add(user)
        models.db.session.commit()
        flash('User %s has been saved.' % request.form['name'])
        return redirect(url_for('manage_users'))

    elif request.method == 'GET' and request.args.get('id') is not None:
        # Display form with existing user information populated
        user = models.User.query.filter(models.User.id == request.args.get('id')).first_or_404()
        return render_template('create_edit_user.html', formdata=user, edit=True)
    else:
        # Display blank form to create new user
        return render_template('create_edit_user.html', formdata=dict())


@app.route('/delete-user/<user_id>', methods=['GET'])
@flask_login.login_required
@get_static_stuff
def delete_user(user_id):
    """Deletes a user."""
    if user_id == session['user_id']:
        flash('Error: you cannot delete your own user account.')
    else:
        user = models.User.query.filter(models.User.id == user_id).first_or_404()
        models.db.session.delete(user)
        models.db.session.commit()
        flash('User has been deleted.')
    return redirect(url_for('manage_users'))


@app.route('/')
@app.route('/posts/')
@app.route('/posts/<permalink>')
@get_static_stuff
def view_posts(permalink=None):
    """Query database for posts and pass them to template. Optional permalink parameter queries for a specific post."""
    if permalink is None:  # Display all recent posts
        # Posts in timeline must be published, and either NOT a static page OR a static page set to display in timeline
        posts = models.Post.query.filter(and_(models.Post.published == True,
                                              or_(models.Post.static_page == False,
                                                  models.Post.static_page_in_timeline == True)))\
            .order_by(models.Post.create_date.desc()).all()
        if not posts:
            flash('No posts yet.')
        return render_template('multiple_posts.html', posts=posts)
    else:  # Permalink is specified, display one post with comments
        if flask_login.current_user.is_authenticated is True:
            # Authenticated user sees post whether or not it is published
            post = models.Post.query.filter_by(permalink=permalink).first_or_404()
        else:
            # Unauthenticated user only sees post if it is published
            post = models.Post.query.filter_by(permalink=permalink, published=True).first_or_404()
        comments = models.Comment.query.filter_by(post_id=post.id)\
            .order_by(models.Comment.create_date_time.desc()).all()
        return render_template('single_post.html', post=post, comments=comments)


@app.route('/unpublished')
@flask_login.login_required
@get_static_stuff
def view_unpublished():
    """Query database for unpublished posts and pass them to template."""
    posts = models.Post.query.filter_by(published=False).order_by(models.Post.create_date.desc()).all()
    if not posts:
        flash('No unpublished posts yet.')
    return render_template('multiple_posts.html', posts=posts, unpublished=True)


@app.route('/site-index')
@get_static_stuff
def site_index():
    """Query database for posts and pass them to template displaying list of links to posts (not full posts)."""
    pages = models.Post.query.filter(and_(models.Post.published == True, models.Post.static_page == True)).all()
    posts = models.Post.query.filter(and_(models.Post.published == True, models.Post.static_page == False)) \
        .order_by(models.Post.create_date.desc()).all()
    if not pages:
        flash('No static pages yet.')
    if not posts:
        flash('No posts yet.')
    return render_template('site_index.html', pages=pages, posts=posts)


@app.route('/posts.atom')
def recent_posts_feed():
    """Generate Atom feed of recent posts."""
    feed = AtomFeed('Recent Posts', feed_url=request.url, url=request.url_root)
    # Posts in feed must be published, and either NOT a static page OR a static page set to display in timeline
    posts = models.Post.query.filter(and_(models.Post.published == True,
                                   or_(models.Post.static_page == False, models.Post.static_page_in_timeline == True)))\
        .order_by(models.Post.create_date.desc()).limit(15).all()
    for post in posts:
        # Todo render markdown
        feed.add(post.title,
                 markdown(post.body),
                 content_type='html',
                 author=post.user_name(),
                 url=urljoin(request.url_root, '/posts/' + post.permalink),
                 updated=post.edit_date,
                 published=post.create_date
                 )
    return feed.get_response()


@app.route('/create', methods=['GET', 'POST'])
@flask_login.login_required
@get_static_stuff
def create_edit_post():
    """Creates and updates a post."""
    if request.method == 'POST':
        if request.form.get('update_id'):
            # Updating existing post in database
            post = models.Post.query.filter_by(id=request.form['update_id']).first_or_404()
            post.title = request.form['title']
            post.body = request.form['body']
            post.description = request.form['description']
            post.permalink = slugify(request.form['permalink'])
            post.static_page = True if request.form['static_page'] == "True" else False
            post.static_page_in_timeline = True if request.form.get('static_page_in_timeline') == "True" else False
            post.static_page_link_title = request.form.get('static_page_link_title')
            post.published = True if request.form.get('published') == "True" else False
            post.comments_allowed = True if request.form.get('comments_allowed') == "True" else False
            post.edit_date = models.datetime.utcnow()
            post.user_id = session['user_id']
        else:
            # Creating new post in database
            post = models.Post(title=request.form['title'],
                               body=request.form['body'],
                               description=request.form['description'],
                               permalink=slugify(request.form['permalink']),
                               static_page=True if request.form['static_page'] == "True" else False,
                               static_page_in_timeline=True if request.form.get('static_page_in_timeline') == "True" else False,
                               static_page_link_title=request.form.get('static_page_link_title'),
                               published=True if request.form.get('published') == "True" else False,
                               comments_allowed=True if request.form.get('comments_allowed') == "True" else False,
                               user_id=session['user_id'])
        try:
            models.db.session.add(post)
            models.db.session.commit()
        except (IntegrityError, InvalidRequestError):
            models.db.session.rollback()
            flash('There was a problem creating your post. Please make sure that another post does not already have '
                  'your desired post title and permalink.')
            return render_template('create_edit_post.html', formdata=request.form)
        else:
            flash('Post successful')
            return redirect(url_for('view_posts', permalink=post.permalink))
    elif request.method == 'GET' and request.args.get('id') is not None:
        # Editing existing post
        post = models.Post.query.filter_by(id=request.args.get('id')).first_or_404()
        return render_template('create_edit_post.html', formdata=post, edit=True)
    elif request.method == 'GET':
        # Composing new post
        return render_template('create_edit_post.html', formdata=dict())


@app.route('/delete-post/<post_id>')
@flask_login.login_required
@get_static_stuff
def delete_post(post_id):
    """Deletes a post."""
    post = models.Post.query.filter_by(id=post_id).first_or_404()
    models.db.session.delete(post)
    models.db.session.commit()
    flash('Post has been deleted.')
    return redirect(url_for('view_posts'))


@app.route('/posts/<permalink>/create-comment', methods=('GET', 'POST'))
@get_static_stuff
def create_comment(permalink):
    """Create a comment on a post."""
    if flask_login.current_user.is_authenticated:
        form = forms.CommentForm(request.form)
        guest = False
    else:
        form = forms.CommentFormGuest(request.form)
        guest = True

    post = models.Post.query.filter_by(permalink=permalink).first_or_404()
    comments = models.Comment.query.filter_by(post_id=post.id).order_by(models.Comment.create_date_time.desc()).all()
    if request.method == 'POST':
        if form.validate_on_submit():
            comment = models.Comment(post_id=post.id,
                                     body=form.body.data,
                                     author_user_id=flask_login.current_user.get_id() if guest is False else None,
                                     guest_author_name=form.guest_author_name.data if guest is True else None,
                                     guest_author_email=form.guest_author_email.data if guest is True else None)
            models.db.session.add(comment)
            models.db.session.commit()
            flash('Your comment has been posted.')
            return redirect(url_for('view_posts', permalink=permalink))
        else:
            flash('There is a problem with your comment, please see below')
            return render_template('create_edit_comment.html', post=post, form=form, comments=comments, guest=guest, edit=False)
    elif request.method == 'GET':
        return render_template('create_edit_comment.html', post=post, form=form, comments=comments, guest=guest, edit=False)


@app.route('/posts/<permalink>/edit-comment', methods=('GET', 'POST'))
@flask_login.login_required
@get_static_stuff
def edit_comment(permalink):
    """Edit an existing comment."""
    post = models.Post.query.filter_by(permalink=permalink).first_or_404()
    comment = models.Comment.query.filter_by(id=request.args.get('id')).first_or_404()
    if comment.author_user_id:
        form = forms.CommentForm(request.form, comment)
        guest = False
    else:
        form = forms.CommentFormEditGuest(request.form, comment)
        guest = True

    if request.method == 'POST':
        if form.validate_on_submit():
            comment.body = form.body.data
            comment.guest_author_name = form.guest_author_name.data if guest is True else None
            comment.guest_author_email = form.guest_author_email.data if guest is True else None
            models.db.session.add(comment)
            models.db.session.commit()
            flash('Comment has been updated.')
            return redirect(url_for('view_posts', permalink=permalink))
        else:
            flash('There is a problem with your comment, please see below')
            return render_template('create_edit_comment.html', post=post, form=form, guest=guest, edit=True)
    if request.method == 'GET' and request.args.get('id') is not None:
        return render_template('create_edit_comment.html', post=post, form=form, guest=guest, edit=True)
    else:
        abort(404)


@app.route('/delete_comment')
@flask_login.login_required
@get_static_stuff
def delete_comment():
    """Delete a comment."""
    comment = models.Comment.query.filter_by(id=request.args.get('id')).first_or_404()
    post = models.Post.query.filter_by(id=comment.post_id).first_or_404()
    models.db.session.delete(comment)
    models.db.session.commit()
    flash('Comment has been deleted.')
    return redirect(url_for('view_posts', permalink=post.permalink))

@app.route('/markdown')
@get_static_stuff
def markdown_reference():
    return render_template('markdown_reference.html')

@app.errorhandler(429)
def rate_limit_exceeded_handler(e):
    """Warns user that they have hit the rate limiter."""
    flash('You have tried doing that too often. Please wait a minute before trying again.')
    # Return statement should be generalized if we ever use rate limiting for actions other than logging in
    return make_response(redirect(url_for('login')))


# Jinja2 display filters
@app.template_filter('date_format')
def date_format(value, formatstr='%Y-%m-%d'):
    """Parses timestamps as a date in ISO 8601 date format."""
    return value.strftime(formatstr)

@app.template_filter('post_preview')
def post_preview(value):
    """Returns a truncated 'preview' of a post for display on the front page."""
    if '$fold$' in value:
        return value.split('$fold$')[0] + '...'
    else:
        return value.split('\n')[0] + '...'


@app.template_filter('render_markdown')
def render_markdown(value):
    """Renders markdown in jinja2 templates, removing the $fold$ marker"""
    return markdown(value).replace('$fold$', '')
