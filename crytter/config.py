import os


class Config:
	SECRET_KEY = '0x0x0x0x0x'#os.environ.get('crytter-secret-key')
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'#os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
	RECAPTCHA_PUBLIC_KEY = '6LftYaYaAAAAAOifwTxOZxkBEg_ZGtQBBoRcoyos'#os.environ.get('RECAPTCHA-PUBLIC-KEY')
	RECAPTCHA_PRIVATE_KEY = '6LftYaYaAAAAAGs01PWgb0-sbjrKkhGDXVQi2cKF'#os.environ.get('RECAPTCHA-SECRET-KEY')
	RECAPTCHA_DATA_ATTRS = {'theme': 'dark'}
	PREFERRED_URL_SCHEME = 'https'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	# MAIL_SERVER = 'smtp.sendgrid.net'
	# MAIL_PORT = 587
	# MAIL_USE_TLS = True
	# MAIL_USERNAME = os.environ.get('crytter-mail-user')
	# MAIL_PASSWORD = os.environ.get('crytter-mail-password')
