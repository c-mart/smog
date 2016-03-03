# smog
Simple Markdown blOG, or chriS Martin's blOG

See a demo blog, which is also my personal blog, at https://smog.c-mart.in. (Todo: host a demo site where people can log in, where the database is rebuilt every hour or so)

- Written in Python using [Flask](http://flask.pocoo.org/) microframework
- Write posts in [Markdown](https://daringfireball.net/projects/markdown/), HTML, or plain text
- Uses [SQLAlchemy](http://www.sqlalchemy.org/) with modular back-end: use any database you like
- HTML5
- Renders nicely without JavaScript support because there is no JavaScript
- Easy to modify and extend, fairly complete test coverage will let you know if you break anything
- GNU GPL

## Story
I wrote this in order to learn Python web development and scratch a personal itch for a blogging engine.

## How to Install on a Web Server (work in progress)

This assumes that you already have a working and reasonably well-secured web server. It doesn't cover setup of HTTPS encryption, but that is very easy if you run [Let's Encrypt](https://letsencrypt.org/getting-started/) after following the setup steps below.

This is written for a Debian/Ubuntu server running Apache 2. Commands will be slightly different on another operating system like RHEL/CentOS.

- Install prerequisite packages: `apt-get install git libapache2-mod-wsgi python python-dev python-pip`
- Clone the project: `git clone https://github.com/c-mart/smog.git` into a directory on your web server (like /var/www/)
- Connect to a real database. (Todo: help people do this.) If you don't, it will create a SQLite database in your /tmp directory, which will probably disappear next time you reboot your server. 
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
- Run `python manage.py db upgrade` to apply latest schema version to your database
- Run `python manage.py populate_db`

## How to Perform Updates
- `git pull` the repo in-place
- Activate smog virtualenv?
- Run `python manage.py db upgrade` to apply latest schema version to your database
- Reload your web server?

## Known Issues
smog does not protect against CSRF. I plan to switch to WTForms which should solve this.

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
- slugify
- mistune

## Acknowledgements
- Default template uses https://en.wikipedia.org/wiki/Tango_Desktop_Project#Palette

## License
Copyright 2016 Chris Martin. smog is free software released under the GNU GPL version 3.