from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from flask_login import current_user
from crytter.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[
		DataRequired(), Length(min=1, max=32),
		Regexp(r'^[a-zA-Z0-9_]*$', message='Usernames can contain only alphanumeric characters and _')
		])
	email = StringField('Email', validators=[
		DataRequired(), Email()
		])
	password = PasswordField('Password', validators=[
		DataRequired()
		])
	confirm_password = PasswordField('Confirm Password', validators=[
		DataRequired(), EqualTo('password', message='Passwords must match.')
		])

	terms = BooleanField('I agree to the Terms & Conditions as well as the Rules & Guidelines of crytter.org', validators=[DataRequired(message='You must agree to create an account.')])

	recaptcha = RecaptchaField(validators=[Recaptcha(message="Prove you are not a robot.")])
	submit = SubmitField('create account')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username already in use.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email already in use.')

class LoginForm(FlaskForm):
	usernameORemail = StringField('Username or Email', validators=[
		DataRequired(), Length(min=1, max=256)
		])
	password = PasswordField('Password', validators=[
		DataRequired()
		])
	remember = BooleanField('Stay logged in?')
	recaptcha = RecaptchaField(validators=[Recaptcha(message="Prove you are not a robot.")])

	submit = SubmitField('Log in')

class UpdateProfileForm(FlaskForm):
	username = StringField('Username', validators=[
		DataRequired(), Length(min=1, max=32),
		Regexp(r'^[a-zA-Z0-9_]*$', message='Usernames can contain only alphanumeric characters and _')])
	email = StringField('Email', validators=[
		DataRequired(), Email()
		])
	biography = TextAreaField('Biography', validators=[
		Length(min=0, max=75),
		Regexp(r'^(?:[\x20-\x7E])+$', message='Irregular characters are not supported in biographies due to impersonation tactics.')
		])

	picture = SelectField('Avatar Color', choices=[
		('default', 'Gray'),
		('default-aqua', 'Aqua'), 
		('default-blue', 'Blue'),
		('default-green', 'Green'),
		('default-orange', 'Orange'),
		('default-pink', 'Pink'),
		('default-red', 'Red')
		],
		 validators=[])

	submit = SubmitField('Update Profile')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username already in use.')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email already in use.')

class UpdatePasswordForm(FlaskForm):
	oldpassword = PasswordField('Current Password', validators=[
		DataRequired()
		])
	newpassword = PasswordField('New Password', validators=[
		DataRequired()])
	confirmnewpassword = PasswordField('Confirm New Password', validators=[
		DataRequired(), EqualTo('newpassword')])

	submit = SubmitField('change password')

class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[
		DataRequired(), Email()])

	recaptcha = RecaptchaField(validators=[Recaptcha(message="Prove you are not a robot.")])

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('No user exists with this email. Consider creating an account.')

	submit = SubmitField('Request password reset')

class ResetPasswordForm(FlaskForm):
	newpassword = PasswordField('New Password', validators=[
		DataRequired()])
	confirmnewpassword = PasswordField('Confirm New Password', validators=[
		DataRequired(), EqualTo('newpassword')])

	submit = SubmitField('reset password')

class RateUserForm(FlaskForm):
	rating = SelectField('Rating:', choices=[
		('+1', 'Positive, I would deal with this user again'), 
		('-1', 'Negative, I would not deal with this user again')
		],
		 validators=[DataRequired()])
	experience = TextAreaField('Describe your experience in dealing with this user:', validators=[DataRequired(), Length(max=256, message='Too long, 256 character limit')])
	recaptcha = RecaptchaField(validators=[Recaptcha(message="Prove you are not a robot.")])

	submit = SubmitField('Submit Rating')