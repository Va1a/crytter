from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from crytter.config import Config
import json

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message = 'Login to access this page...'
login_manager.login_message_category = 'warning'

mail = Mail()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)
	app.jinja_env.globals.update(json=json)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)

	from crytter.users.routes import users
	from crytter.posts.routes import posts
	from crytter.main.routes import main
	from crytter.errors.handlers import errors
	app.register_blueprint(users)
	app.register_blueprint(posts)
	app.register_blueprint(main)
	app.register_blueprint(errors)
	
	return app