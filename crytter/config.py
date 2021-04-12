import os


class Config:
	SECRET_KEY = os.environ.get('flask-secret-key')
	SQLALCHEMY_DATABASE_URI = os.environ.get('flask-sqlalchemy-database-uri')
	# SERVER_NAME = 'crytter.org'
	RECAPTCHA_PUBLIC_KEY = '6LftYaYaAAAAAOifwTxOZxkBEg_ZGtQBBoRcoyos'
	RECAPTCHA_PRIVATE_KEY = '6LftYaYaAAAAAGs01PWgb0-sbjrKkhGDXVQi2cKF'
	RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}
	PREFERRED_URL_SCHEME = 'https'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get('flask-mail-user')
	MAIL_PASSWORD = os.environ.get('flask-mail-password')
