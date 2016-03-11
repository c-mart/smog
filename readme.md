# smog
Simple Markdown blOG, or chriS Martin's blOG

See a demo blog, which is also my personal blog, at https://smog.c-mart.in. (Todo: host a demo site where people can log in, where the database is rebuilt every hour or so)

## Features for Users

- Write posts in [Markdown](https://daringfireball.net/projects/markdown/), plain text, or HTML. Markdown is a very simple markup language that allows you to easily format and enrich your content.
- Create both blog posts and static pages. This is ideal for a web site with a mix of regular/new content and permanent/curated content like project pages
- Supports multiple content authors, each with their own account
- Comments can be enabled/disabled per post and guest comments are easy to moderate. A Recaptcha limits the amount of spam comments that you'll deal with.
- Super mobile-friendly

## Features for Developers

- Written in Python using [Flask](http://flask.pocoo.org/) microframework
- Uses [SQLAlchemy](http://www.sqlalchemy.org/) with modular back-end: use any database you like
- Built-in database migrations (using [Flask-Migrate](https://flask-migrate.readthedocs.org/en/latest/)) allows you to easily update the database of your deployed Flask application when new features are added in the future
- Guest input is validated using [WTForms](http://wtforms.readthedocs.org/en/latest/)
- Renders nicely without JavaScript support
- Easy to modify and extend, fairly complete test coverage will let you know if you break anything
- GNU GPL

## Story
I wrote this in order to learn Python web development and scratch a personal itch for a blogging engine.

If you're looking for a lean and simple blog platform with clean styling that works equally well for micro- and macro-blogging, smog is for you. If you're looking to download and apply a bunch of pre-made, gaudy themes to your site, smog is not for you.

## How to Install on a Web Server (work in progress)
If you already know how to configure and administer a Unix/Linux web server then Smog is easy to configure. If you don't feel comfortable on the command line then these instructions will probably disappoint.

Hardening the server, updates, and backups are up to you. This also doesn't cover setup of HTTPS encryption, but that is very easy if you run [Let's Encrypt](https://letsencrypt.org/getting-started/) after following the setup steps below.


This is written for a Debian/Ubuntu server running Apache 2. Commands will be slightly different on another operating system like RHEL/CentOS.

- Install prerequisite packages: `apt-get install git libapache2-mod-wsgi python python-dev python-pip`
- Clone the project: `git clone https://github.com/c-mart/smog.git` into a directory on your web server (like /var/www/)
- Connect to a real database. (Todo: tell people how to do this.) If you don't, it will create a SQLite database in your /tmp directory, which will probably disappear next time you reboot your server. 
- Enable WSGI Apache module: `a2enmod wsgi`
- Install virtualenv: `pip install virtualenv`
- Create a virtualenv: `virtualenv /var/www/smog-venv` (or any other path you wish your virtualenv to live in)
- Install dependencies: `pip install Flask flask_sqlalchemy flask_login flask_limiter slugify mistune`
- Create /etc/apache2/sites-available/smog.conf (todo upload example of this)
- Create your WSGI file, e.g. at /var/www/smog.wsgi (todo upload example of this, perhaps from http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/)
- Enable the site: `a2ensite smog`
- Reload apache: `service apache2 reload`
- Try browsing to your site, if everything is working the page will load.
- Log in with test account, username "test@test.com" and password "changeme123". **The first thing you should do is navigate to Manage Users, then change the user name and password for your account.** (todo make this more secure by default)
- Browse to Site Settings, customize the name of your blog and your desired footer line
- Start blogging

Other (integrate this):

- Create config file containing things like SQLALCHEMY_DATABASE_URI and SECRET_KEY
- In your WSGI file, set SMOG_CONFIG environment variable pointing to your config file, e.g. `os.environ['SMOG_CONFIG'] = '/var/www/smog_config'`
- Activate your virtual environment and run `python manage.py init_db` to add a test user and populate initial site settings

## How to Perform Updates
- `git pull` the repo in-place
- Activate smog virtualenv
- Set your SMOG_CONFIG environment variable
and run `python manage.py db upgrade` to apply latest schema version to your database
- Reload your web server?

## Known Issues
Automatic database schema updates in the future (using Flask-Migrate) may not work if you're using a SQLite back-end. Use another database engine instead, like MySQL or PostgreSQL. (This is because SQLite doesn't natively support adding and removing columns from a table, and Flask-Migrate hasn't yet implemented a workaround.)

smog does not protect against [CSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery). I plan to switch to WTForms which should solve this.

smog is not yet recommended for blog admins that don't completely trust their authors (authenticated users) with admin-level site access, for two reasons:
- There is currently no separation of privileges between users. Any authenticated user can CRUD other user accounts.
- When a user account is disabled, the disabled user is not prevented from doing anything until he or she logs out.

If you will be the only post author, or you will only have a handful of trusted users, then rock on.


## Dependencies
All of these should be available from PyPI/pip:
- flask
- flask_sqlalchemy
- flask_script
- flask_migrate
- flask_login
- flask_limiter
- Flask-WTF
- slugify
- mistune

## Acknowledgements
- Default template uses https://en.wikipedia.org/wiki/Tango_Desktop_Project#Palette

## License
Copyright 2016 Chris Martin. smog is free software released under the GNU GPL version 3.