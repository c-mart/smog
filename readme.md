# smog: Simple Markdown blOG
smog is intended to be a lightweight yet feature-complete blog platform for individuals and organizations. I wrote smog in about 60 hours to learn web development using Python and the [Flask](http://flask.pocoo.org/) microframework, after trying other blog platforms and deciding they weren't for me.

See a real live example (also my personal blog) at https://smog.c-mart.in.
Play with a demo site at http://smogdemo.c-mart.in. Log in with username 'test@test.com' and password 'test', create some posts and play with the settings. (Demo site is rebuilt from scratch every 30 minutes, if you're having trouble just try again in half an hour.)
Docker image is not secure!

I want smog to be a pleasure for bloggers, readers, and also developers who want to tweak or extend what their blog can do.

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

## How to Install on a Web Server (work in progress)
If you already have experience configuring and administering a Unix/Linux server, then smog is easy to set up. If you don't, then these instructions will probably disappoint; I recommend you obtain assistance from someone who knows what they are doing. (smog isn't currently packaged for easy setup by non-technical folks, though that could change in the future!)

Hardening the server, updates, and backups are up to you. This also doesn't cover setup of HTTPS encryption, but that is very easy if you run [Let's Encrypt](https://letsencrypt.org/getting-started/) after following the setup steps below.

This is written for a Debian/Ubuntu server running Apache. Commands will be slightly different on another operating system like RHEL/CentOS.

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
- Start blogging!

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

## Is smog right for me? / Known Issues
Automatic database schema updates in the future (using Flask-Migrate) may not work if you're using a SQLite back-end. Use another database engine instead, like MySQL or PostgreSQL. (This is because SQLite doesn't natively support adding and removing columns from a table, and Flask-Migrate hasn't yet implemented a workaround.)

smog does not protect against [CSRF](https://en.wikipedia.org/wiki/Cross-site_request_forgery). I plan to switch to WTForms which should solve this.

smog is not yet recommended for blog admins that don't completely trust their authors (authenticated users) with admin-level site access, for two reasons:
- There is currently no separation of privileges between users. Any authenticated user can CRUD other user accounts.
- When a user account is disabled, the disabled user is not prevented from doing anything until he or she logs out.

If you will be the only post author, or you will only have a handful of trusted users, then rock on.

## Dependencies
See requirements.txt

## Acknowledgements
- Default template uses https://en.wikipedia.org/wiki/Tango_Desktop_Project#Palette

## License
Copyright 2016 Chris Martin. smog is free software released under the GNU GPL version 3.