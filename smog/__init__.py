from flask import Flask
from flask.ext.misaka import Misaka
from os import path
from smog.helpers import *
from flask_sqlalchemy import SQLAlchemy
import flask_login
import flask_limiter

# Initializing application and extensions
app = Flask(__name__)
app.config.from_object('smog.config_run')
Misaka(app)
db = SQLAlchemy(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
limiter = flask_limiter.Limiter()
limiter.init_app(app)
import smog.views



def init_db():
    import smog.models
    db.create_all()
    testuser = models.User('test@test.com', 'Test User', 'changeme123')
    db.session.add(testuser)
    db.session.commit()

# Create database if it's not there
if not path.exists(app.config['DB_PATH']):
    init_db()

if __name__ == '__main__':
    app.run()
