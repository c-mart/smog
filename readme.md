# smog: Simple Markdown blOG
smog is intended to be a lightweight yet feature-complete blog platform for individuals and organizations. I wrote smog in about 60 hours to learn web development using Python and the [Flask](http://flask.pocoo.org/) microframework, after trying other blog platforms and deciding they weren't for me. I want smog to be a pleasure for bloggers, readers, and also developers who want to tweak or extend what their blog can do.

See a real live example (also my personal blog) at https://smog.c-mart.in.

## Why you may like smog as a blogger

- **Write posts in Markdown**, plain text, or HTML
- Create **blog posts and static pages**; ideal for a web site with a mix of regular/new content and permanent/curated content like project pages or your resume
- Supports **multiple content authors**, each with their own account
- Guest comments are protected with a CSRF token and [reCAPTCHA](https://www.google.com/recaptcha/intro/index.html), which **drastically limits the number of spam comments** you'll need to deal with
- **Comments** can be enabled/disabled per post and are easy to moderate
- Super **mobile-friendly**. Also **renders nicely without JavaScript**, because some people don't want to run your JavaScript

## Why you may like smog as a developer

- Written in Python using [Flask](http://flask.pocoo.org/) microframework and several of its extensions
- Easy to modify and extend, fairly complete test coverage will let you know if you break stuff
- Uses [SQLAlchemy](http://www.sqlalchemy.org/) with modular back-end: use any database you like
- Built-in database migrations (using [Flask-Migrate](https://flask-migrate.readthedocs.org/en/latest/)) allows you to update the database of your deployed blog when new features are added to smog
- Input validation using [WTForms](http://wtforms.readthedocs.org/en/latest/)
- Complete source only ~200 KB (as of March 2016)
- GNU GPL licensed

## Try Smog
### Demo Site
**[http://smogdemo.c-mart.in](http://smogdemo.c-mart.in)**

- Username: 'test@test.com'
- Password: 'test'

Here you can create some posts and play with the settings. The demo site is automatically destroyed and re-created every 30 minutes, so if you're having trouble just try again in half an hour.

### Docker Image
If you have Docker installed, you can download and run a own demo copy of smog with just one command:

    docker run --name smog -p 80:5000 cmart/smog-demo

Then, browse to http://localhost and you should have a demo site running. Log in with username 'test@test.com' and password 'test'.

WARNING: the smog-demo docker image is for evaluation purposes and not secured for production use. It runs as a privileged user, uses the default Flask development WSGI server with default secret keys, and doesn't have HTTPS support. Please do not trust it with any sensitive data or leave it exposed to the internet.

## How to Install smog In Production
See [install_guide.md](https://github.com/c-mart/smog/blob/master/install_guide.md).

## How to Perform Updates
Future database schema changes probably won't work if you're running a SQLite database. If you're using MySQL or PostgreSQL, update on:

- `cd` to your smog repository folder and run `git pull` to update the repository
- Activate your smog virtualenv, e.g.:
- `source /var/www/smog-venv/bin/activate`)
- Set your SMOG_CONFIG environment variable to point to your configuration file, e.g.:
- `SMOG_CONFIG=/var/www/smog_config.py`)
- Run the database upgrade script to apply latest schema version:
- `python manage.py db upgrade`
- Restart your web server:
- (sudo) `service apache2 restart`

## Is smog right for me? / Known Issues
smog does not yet fully protect against [CSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery). This will change when WTForms is fully integrated with the site.

smog is not yet recommended for blog admins that don't completely trust their authors (authenticated users) with admin-level site access, for two reasons:
- There is currently no separation of privileges between users. Any authenticated user can CRUD other user accounts.
- When a user account is disabled, the disabled user is not prevented from doing anything until he or she logs out.

If you will be the only post author, or you will only have a handful of trusted users, then rock on.

## Dependencies
Python 2.7.8 or later, and the modules listed in requirements.txt

## Acknowledgements
- Default template uses https://en.wikipedia.org/wiki/Tango_Desktop_Project#Palette

## License
Copyright 2016 Chris Martin. smog is free software released under the GNU GPL version 3.