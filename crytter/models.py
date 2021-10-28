from crytter import db, login_manager
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Rating(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	ratee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	date_rated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	impact = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f'Rating("{self.rater}", "{self.ratee}", "{self.content}")'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(32), unique=True, nullable=False)
	email = db.Column(db.String(256), unique=True, nullable=False)
	rating = db.Column(db.Integer, nullable=False, default=0)
	rateBar = db.Column(db.String, nullable=False, default='<a href="/help/rating-badge" class="mr-1 btn btn-secondary btn-xs" >New User</a>')
	date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	biography = db.Column(db.Text, nullable=False, default='')
	image_file = db.Column(db.String, nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	permission_level = db.Column(db.Integer, nullable=False, default=0)
	last_search = db.Column(db.String(128), nullable=False, default='')
	posts = db.relationship('Post', backref='author', lazy=True)
	comments = db.relationship('Comment', backref='author', lazy=True)
	badges = db.relationship('Badge', backref='bearer', lazy=True)
	alerts = db.relationship('Alert', backref='assoc_user', lazy=True)
	ratesOfOthers = db.relationship('Rating', backref='rater', foreign_keys=[Rating.rater_id], lazy=True)
	ratingsByOthers = db.relationship('Rating', backref='ratee', foreign_keys=[Rating.ratee_id], lazy=True)


	def get_reset_token(self, expirySec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expirySec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)


	def __repr__(self):
		return f'User("{self.username}", "{self.email}", "{self.image_file}")'

class Alert(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(128), nullable=False)
	seen = db.Column(db.Boolean, nullable=False, default=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	from_user = db.Column(db.Integer, nullable=False, default=0)
	from_username = db.Column(db.String(32), nullable=False, default='')
	post_id = db.Column(db.Integer, nullable=False, default=0)
	post_title = db.Column(db.String(128), nullable=False, default='')

	def __repr__(self):
		return f'Alert("{self.type}", "{self.user_id}", "{self.seen}")'

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sticky = db.Column(db.Boolean, nullable=False, default=False)
	wanted = db.Column(db.String(10), nullable=False)
	giving = db.Column(db.String(10), nullable=False)
	amountWanted = db.Column(db.Float, nullable=False)
	amountGiving = db.Column(db.Float, nullable=False)
	title = db.Column(db.String(128), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	comments = db.relationship('Comment', backref='assoc_post', lazy=True)

	def __repr__(self):
		return f'Post("{self.title}", "{self.date_posted}")'


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text, nullable=False)
	date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f'Comment("{self.date_commented}", "{self.post_id}", "{self.user_id}")'

class Badge(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	html = db.Column(db.String, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	date_recieved = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return f'Badge("{self.name}", "{self.html}", "{self.user_id}")'
