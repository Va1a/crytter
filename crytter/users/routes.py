from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from crytter import db, bcrypt
from crytter.models import User, Post, Comment, Alert, Badge, Rating
from crytter.users.forms import RegistrationForm, LoginForm, UpdateProfileForm, UpdatePasswordForm, RequestResetForm, ResetPasswordForm, RateUserForm
from crytter.users.utils import verifyPerms, rateToHTML #, send_reset_email

users = Blueprint('users', __name__)

# REGISTER A NEW ACCOUNT
@users.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashedpw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data,email=form.email.data,password=hashedpw)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been made, {form.username.data}. You can now login.', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register for a DKYP account', form=form)

#LOGIN TO EXISTING ACCOUNT
@users.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
			user = User.query.filter_by(username=form.usernameORemail.data).first()
			if not user:
				user = User.query.filter_by(email=form.usernameORemail.data).first()
			if user and bcrypt.check_password_hash(user.password, form.password.data):
				if not verifyPerms(user):
					flash('Your account has been locked. Email lockout@dkyp.net for assistance.', 'danger')
				else:
					login_user(user, remember=form.remember.data)
					nextpage = request.args.get('next')
					flash(f'Logged in as {user.username}.', 'success')
					return redirect(nextpage) if nextpage else redirect(url_for('main.home'))
			else:
				flash('Invalid Credentials.', 'danger')
	return render_template('login.html', title='Login to your DKYP account', form=form)

#LOGOUT CURRENTLY LOGGED IN ACCOUNT
@users.route('/logout')
def logout():
	logout_user()
	flash('You have been logged out.', 'success')
	return redirect(url_for('users.login'))

@users.route('/profile')
@login_required
def userpage_redirect():
	return redirect(url_for('users.userpage', username=current_user.username)), 302

# EDIT PROFILE PAGE
@users.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile():
	form = UpdateProfileForm()
	if form.validate_on_submit():
		current_user.image_file = form.picture.data+'.jpg'
		current_user.username = form.username.data
		current_user.email = form.email.data
		current_user.biography = form.biography.data
		db.session.commit()
		flash('Profile Updated!', 'success')
		return redirect(url_for('users.profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.biography.data = current_user.biography
		form.picture.data = current_user.image_file[:-4]
	imagefile = url_for('static', filename=f'profile_pics/{current_user.image_file}')
	return render_template('profile.html', title='Edit your profile', imagefile=imagefile, form=form)

# VIEW YOUR ALERTS
@users.route('/alerts')
@login_required
def alerts():
	page = request.args.get('p', 1, type=int)
	alerts = Alert.query.filter_by(assoc_user=current_user).order_by(Alert.date.desc()).paginate(page=page, per_page=10)
	for alert in alerts.items:
		try:
			alert.from_username = User.query.get(alert.from_user).username
			if alert.type == 'comment':
				alert.post_title = Post.query.get(alert.post_id).title
		except AttributeError:
			db.session.delete(alert)
			db.session.commit()
	# we render the template before we change the alerts to all seen
	prerendered_template = render_template('alerts.html', title='Alerts', alerts=alerts)
	for alert in alerts.items:
		alert.seen = True
	db.session.commit()
	return prerendered_template

@users.route('/alerts/<string:operation>', methods=['POST', 'GET'])
@login_required
def alert_settings(operation):
	if operation == 'clear-all' and request.method == 'POST':
		alerts = Alert.query.filter_by(assoc_user=current_user).all()
		for alert in alerts:
			db.session.delete(alert)
		flash('Cleared all alerts.', 'success')
	elif operation == 'clear-only' and request.method == 'GET':
		alert = Alert.query.get(request.args.get('alert', None, type=int))
		if not alert: abort(404)
		if alert.assoc_user != current_user: abort(403)
		db.session.delete(alert)
		flash('Cleared alert.', 'success')
	else: abort(404)
	db.session.commit()
	return redirect(url_for('users.alerts'))

# PUBLIC PROFILE PAGE
@users.route('/user/<string:username>')
def userpage(username):
	page = request.args.get('p', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

	return render_template('userpage.html', posts=posts, user=user, title=user.username, description=f'Profile of {user.username} - {user.rating} reputability. {user.biography}')


# USER RATINGS
@users.route('/user/<string:username>/ratings', methods=['GET', 'POST'])
def ratings(username):
	page = request.args.get('p', 1, type=int)
	form = RateUserForm()
	user = User.query.filter_by(username=username).first_or_404()
	oldReview = (Rating.query.filter_by(rater=current_user, ratee=user).first() if current_user.is_authenticated else None)
	ratings = Rating.query.filter_by(ratee=user).order_by(Rating.date_rated.desc()).paginate(page=page, per_page=5)
	if oldReview and request.method == 'GET':
		form.rating.data = ('+1' if oldReview.impact > 0 else '-1')
		form.experience.data = oldReview.content
	if form.validate_on_submit():
		if not current_user.is_authenticated or current_user == user: abort(403)
		if oldReview: 
			db.session.delete(oldReview)
			user.rating -= oldReview.impact

		ratePower = current_user.rating // 10
		if current_user.rating >= 0 and ratePower == 0: ratePower = 1
		if current_user.rating < 0: ratePower = 0
		if form.rating.data == '+1':
			newRating = Rating(ratee=user, rater=current_user, impact=int(ratePower), content=form.experience.data)
			user.rating += ratePower
		else:
			newRating = Rating(ratee=user, rater=current_user, impact=int(ratePower)*-1, content=form.experience.data)
			user.rating -= ratePower
		alert = Alert(assoc_user=user, type='rating', from_user=current_user.id, post_id=0)
		db.session.add(newRating)
		db.session.add(alert)
		user.rateBar = rateToHTML(user.rating)
		db.session.commit()
		flash(f'Rating {"Updated" if oldReview else "Submitted"}', 'success')
		return redirect(url_for('users.ratings', username=user.username))
	return render_template('ratingsreceived.html', ratings=ratings, user=user, form=form, oldReview=oldReview, title=user.username+' / ratings', description=f'{user.username} ratings - {user.rating} reputability')

# RATINGS GIVEN BY USER TO OTHERS
@users.route('/user/<string:username>/ratings-given')
def ratingsGiven(username):
	page = request.args.get('p', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	ratings = Rating.query.filter_by(rater=user).order_by(Rating.date_rated.desc()).paginate(page=page, per_page=5)
	return render_template('ratingsgiven.html', ratings=ratings, user=user, title=user.username+' / given ratings', description=f'{user.username} - ratings given to others')


# CHANGE PASSWORD PAGE
@users.route('/profile/password', methods=['GET', 'POST'])
@login_required
def changePassword():
	form = UpdatePasswordForm()
	if form.validate_on_submit() and bcrypt.check_password_hash(current_user.password, form.oldpassword.data):
		hashedpw = bcrypt.generate_password_hash(form.newpassword.data).decode('utf-8')
		current_user.password = hashedpw
		db.session.commit()
		flash('Password Updated!', 'success')
		return redirect(url_for('users.profile'))
	elif form.validate_on_submit() and not bcrypt.check_password_hash(current_user.password, form.oldpassword.data):
		flash('Invalid old password!', 'danger')
	return render_template('changePassword.html', title='Change your Password', form=form)

# FORGOT PASSWORD PAGE (SCRAPPED! (SENDGRID IS EXPENSIVE!!!))
# @users.route('/forgot', methods=['GET', 'POST'])
# def forgot():
# 	if current_user.is_authenticated:
# 		return redirect(url_for('users.profile'))
# 	form = RequestResetForm()
# 	if form.validate_on_submit():
# 		user = User.query.filter_by(email=form.email.data).first()
# 		send_reset_email(user)
# 		flash('Password reset email sent. Please check junk/spam folders if the email does not appear in your inbox.', 'info')
# 		return redirect(url_for('users.login'))
# 	return render_template('forgot.html', title='Reset Password', form=form)

#FORGOT PASSWORD RESET PAGE
#Note that users are unable to reset their passwords via email. 
#However, this route endpoint is not being removed as there may be a situation where
#an administrator wants to generate a reset token.
@users.route('/forgot/<token>', methods=['GET', 'POST'])
def resetPassword(token):
	if current_user.is_authenticated:
		return redirect(url_for('users.profile'))
	user = User.verify_reset_token(token)
	if not user:
		abort(404)
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashedpw = bcrypt.generate_password_hash(form.newpassword.data).decode('utf-8')
		user.password = hashedpw
		db.session.commit()
		flash('Password updated, you may now log in.', 'success')
		return redirect(url_for('users.login'))
	return render_template('forgot-reset.html', title='Reset Password', form=form)