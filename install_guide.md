## Overview
This will help you get smog running for real production use. Instructions are written for people who feel comfortable administering a Unix/Linux server. If that's not you then you may struggle with this guide. (smog isn't currently packaged for easy setup in production by non-technical folks, though that could change in the future!)

This is written for a Debian/Ubuntu server, which may also be called a VPS, droplet, or instance depending on your cloud provider. If you don't have a server, you can get one for cheap (in some cases free) from Linode, Amazon EC2, or DigitalOcean.

If you are not running as root then you will need to prepend `sudo` to commands that require root privileges as indicated below. Steps for RPM-based distros like CentOS are similar, but with a few more changes (e.g. yum instead of apt-get).

Other sysadmin tasks that you may wish to perform, which this guide does *not* cover:
- Configure DNS for your domain so that people can browse to your site (basically, just add an "A" record for your blog's hostname that points to the IP address of your server).
- Configure a database engine like MySQL or PostgreSQL. SQLite will work to get started and doesn't require much configuration, but *you won't be able to use smog's built-in database migrations if you want to upgrade later on*, due to limitations with SQLite.
- Set up HTTPS encryption, which is very easy if you run [Let's Encrypt](https://letsencrypt.org/getting-started/) after following the setup steps below
- Secure the server (e.g. lock down SSH access, disable unneeded services, run smog as its own user if you have multiple sites and want separation of privileges).
- Configure backups for filesystem and database.
- Run periodic updates for the OS, Python packages installed via pip, and smog itself.

## Python Version
First, check your Python version with `python -V`. smog requires Python 2.7.8 or newer. If your server runs Debian 8 (Jessie) then you can skip this section, but with Ubuntu 14.04 LTS, you're probably on Python 2.7.6, in which case you can use Felix Krull's [Python 2.7 updates](https://launchpad.net/~fkrull/+archive/ubuntu/deadsnakes-python2.7) repository for Ubuntu. (If you do this, read Felix's warning before running the following commands.)

- (sudo) `add-apt-repository ppa:fkrull/deadsnakes-python2.7`
- (sudo) `apt-get update && apt-get -y install python2.7`

With that sorted, let's proceed.

## Server Prep
- Install prerequisite packages:
- (sudo) `apt-get update && apt-get -y install apache2 libapache2-mod-wsgi git python python-dev python-pip python-virtualenv`
- Change to the directory where you want to install smog, like /var/www
- Clone the project repository:
- `git clone https://github.com/c-mart/smog.git`
- From the repository folder that you just cloned, copy smog/smog/config_default.py to another location, name it something like smog_config.py. (This is the file you'll use to configure your site.)
- `cp /var/www/smog/smog/config_default.py /var/www/smog_config.py`

## Edit smog_config.py
Change the value for SQLALCHEMY_DATABASE_URI to tell smog how to connect to your database. This should be formatted as a [SQLAlchemy database URL](http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html#database-urls).

If you don't want to set up a database engine like MySQL or PostgreSQL (and are OK with the caveats above), you can just specify a SQLite file, e.g. `SQLALCHEMY_DATABASE_URI = 'sqlite:////var/www/smogdb/smog.sqlite'`. The user that Apache uses to run smog needs to have read and write access to the folder in which the .sqlite file lives, so I recommend that you place it in its own folder which can be owned by that user. Whatever you do, don't leave the default setting with the database stored in /tmp, which will disappear next time you reboot your server!

Change the value for SECRET_KEY to a random unique string. This is used to encrypt the session cookies that you use to authenticate your users.

Go sign up for [ReCAPTCHA](http://www.google.com/recaptcha/admin), then replace the values for RECAPTCHA_PUBLIC_KEY and RECAPTCHA_PRIVATE_KEY with your real ReCAPTCHA API keys.

Save and close your config file.

## Create Virtual Environment and Install Dependencies
We'll use a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for smog to store our Python interpreter and dependencies. This way they won't conflict with (or be overwritten by) other Python applications that you may run on your server.

- Create a virtualenv:
- `virtualenv /var/www/smog-venv` (or any other path you wish your virtualenv to live in)
- Activate your virtualenv in the shell:
- `source /var/www/smog-venv/bin/activate`
- Install smog's dependencies in your virtualenv:
- `pip install -r /var/www/smog/requirements.txt` (again, change this file path if you cloned smog to somewhere else)

## Configure WSGI file and Apache
The following steps were loosely adapted from [this](http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/) guide in the Flask documentation. If you have trouble configuring Apache, that's a good place to look.

Create your WSGI file at a place like /var/www/smog.wsgi. This is the Python file that apache runs to load your site. An example WSGI file follows, change the folder paths if you need to.

    #!/usr/bin/python
    import os
    import sys
    import logging
    
    activate_this = '/var/www/smog-venv/bin/activate_this.py'  # Change path to your virtualenv if necessary
    execfile(activate_this, dict(__file__=activate_this))
    sys.path.insert(0,"/var/www/smog")  # Change path to your smog folder if necessary
    os.environ['SMOG_CONFIG'] = '/var/www/smog_config.py'  # Change path to your smog config file if necessary
    from smog import app as application

Create a VirtualHost file for Apache, `/etc/apache2/sites-available/smog.conf`. An example of this file follows. Change the ServerName to the domain/hostname of your blog as you configure in DNS. Edit the directory fields to reflect the location of your smog repository folder and WSGI file if you placed them somewhere else.

    <VirtualHost *:80>
            ServerName myblog.c-mart.in
            WSGIScriptAlias / /var/www/smog.wsgi
            <Directory /var/www/smog/smog/>
                    Order allow,deny
                    Allow from all
            </Directory>
            Alias /static /var/www/smog/smog/static
            <Directory /var/www/smog/smog/static/>
                    Order allow,deny
                    Allow from all
            </Directory>
            ErrorLog ${APACHE_LOG_DIR}/error.log
            LogLevel warn
            CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>


- Enable WSGI Apache module: (sudo) `a2enmod wsgi`
- Enable the site: (sudo) `a2ensite smog`
- Reload apache: (sudo) `service apache2 restart`

## Initialize Database
Ensure that your virtualenv is still activated in the shell. Activate it again if necessary (`source /var/www/smog-venv/bin/activate`).

If you are using a SQLite database, create the folder for your database:

`mkdir /var/www/smogdb`

Set an environment variable for your smog configuration file:

`export SMOG_CONFIG=/var/www/smog_config.py`

Run the database initialization routine. This creates the database tables, adds a user, and populates initial site settings.

(sudo) `python /var/www/smog/manage.py init_db`

If you are using a SQLite database, we need to change its file/folder permissions so that the Apache user can write to it:

(sudo) `chown -R www-data:www-data /var/www/smogdb`

## Final Steps
Try browsing to your site. if everything is working your new blog will load.

The first thing you should do is log in with the test account, username "test@test.com" and password "test". Navigate to Manage Site -> Manage Users, then change the email and password for the account to make it yours.

You can also browse to Site Settings to customize the name of your blog and your footer line.

## I'm Stuck!
If you're trying to load your blog and you get an "Internal Server Error",  temporarily add `debug = True` to your smog_config.py file and restart Apache with (sudo) `service apache2 restart`. Then, try loading the page that's not working again, and look at your Apache error log (/var/log/apache2/error.log), it will probably tell you what the problem is. When you're done troubleshooting, be sure to remove the `debug = True` and restart Apache again.

If you're still stuck, contact me (Chris Martin) or submit an issue on the GitHub repository, and I'll help you out.