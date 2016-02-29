# smog
Simple Markdown blOG, or chriS Martin's blOG

- Built with Python using Flask microframework
- Write posts in Markdown or HTML
- SQLAlchemy with modular back-end, use any database you want
- HTML5
- Renders nicely without JavaScript because there is no JavaScript
- GNU GPL

For demo blog, see https://update.me.later

## How to Install on a Web Server (work in progress)

This assumes that you already have a working and reasonably well-secured web server. It doesn't cover setup of HTTPS encryption, but that is very easy if you run [Let's Encrypt](https://letsencrypt.org/getting-started/) after following the setup steps below.

This is written for Debian/Ubuntu running Apache 2. Commands will be slightly different on another OS like RHEL/CentOS.

- Install prerequisite packages: `apt-get install git libapache2-mod-wsgi python python-dev python-pip`
- Clone the project: `git clone https://github.com/c-mart/smog.git` into a directory on your web server (like /var/www/)
- Enable WSGI Apache module: `a2enmod wsgi`
- Install virtualenv: `pip install virtualenv`
- Create a virtualenv: `virtualenv /var/www/smog-venv` (or any other path you wish your virtualenv to live in)
- Install dependencies: `pip install Flask flask_sqlalchemy flask_login flask_limiter slugify mistune`
- Create /etc/apache2/sites-available/smog.conf (todo upload example of this)
- Create your WSGI file, e.g. at /var/www/smog.wsgi (todo upload example of this)
- Enable the site: `a2ensite smog`
- Reload apache: `service apache2 reload`
- Try browsing to your site, if everything is working the page will load.
- Log in with test account, username "test@test.com" and password "changeme123". The first thing you should do is navigate to Manage Users and change the password. (todo make this more secure by default)
- Browse to Site Settings, customize the name of your blog and your desired footer line
- Start blogging

## Story
I wrote this in order to learn Python web development and scratch a personal itch for a blogging engine.

## Known Issues
- We're not adequately protecting against CSRF. Plan to switch to WTForms.
- Currently no separation of privileges between users. Any user can CRUD other user accounts. (This isn't a problem if there is only one user or all users trust each other.)
- When a user account is disabled, the disabled user is not prevented from doing anything until he or she logs out. Until this is fixed, smog is probably not a good choice for folks that want the ability to instantly shut off a given user's access.

## Dependencies
All of these should be available from PyPI/pip:
- Flask
- flask_sqlalchemy
- flask_login
- flask_limiter
- slugify
- mistune

## Acknowledgements
- Mistune Markdown interpreter
- Default template uses https://en.wikipedia.org/wiki/Tango_Desktop_Project#Palette

## License
Copyright 2016 Chris Martin. smog is free software released under the GNU GPL version 3.