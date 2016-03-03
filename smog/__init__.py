from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login
import flask_limiter

# Initializing application and extensions
app = Flask(__name__)
app.config.from_object('smog.config_default')
app.config.from_envvar('SMOG_CONFIG', silent=True)
db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
limiter = flask_limiter.Limiter()
limiter.init_app(app)

import smog.views

if __name__ == '__main__':
    app.run()