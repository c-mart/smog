from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
import flask_login
import flask_limiter

# Initializing application and extensions
app = Flask(__name__)
app.config.from_object('smog.config_default')
app.config.from_envvar('SMOG_CONFIG', silent=True)
print app.config['SQLALCHEMY_DATABASE_URI']
db = SQLAlchemy(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
limiter = flask_limiter.Limiter()
limiter.init_app(app)
import smog.views


def init_db():
    """Creates database for new site, adds a test user and creates default site settings"""
    import smog.models
    db.create_all()
    testuser = models.User('test@test.com', 'Test User', 'changeme123')
    db.session.add(testuser)
    settings = models.SiteSettings()
    db.session.add(settings)
    db.session.commit()

# Create database if it's not there
# TODO fix this now that we no longer have DB_PATH
'''
if not path.exists(app.config['DB_PATH']):
    init_db()
'''

if __name__ == '__main__':
    app.run()
