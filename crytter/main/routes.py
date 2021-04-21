from flask import render_template, send_from_directory, request, Blueprint, abort, flash, redirect, url_for
from flask_login import current_user
from jinja2 import TemplateNotFound
from sqlalchemy import func

from crytter.models import User, Post, Badge, Rating, Comment, Alert
from crytter.main.forms import SearchForm, AssignBadgeForm, RevokeBadgeForm, PermissionsForm, ChangeEmailForm, StickyPostForm, DeleteUserForm
from crytter.main.utils import getSearchResults
from crytter import db

from datetime import date
import json

main = Blueprint('main', __name__)

# HOME PAGE
@main.route('/')
def index():
	today = Post.query.filter(func.date(Post.date_posted) == date.today()).count()
	newest = Post.query.order_by(Post.date_posted.desc()).limit(3).all()
	return render_template('index.html', numToday=today, newest=newest, title='Peer-to-Peer currency trading network')

# POSTS PAGE
@main.route('/posts')
def home():
	page = request.args.get('p', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', posts=posts, title='Offer Index')

# ABOUT PAGE
@main.route('/about')
def about():
	return render_template('about.html', title='about')

# SEO ROBOTS.TXT
@main.route('/robots.txt')
def robots():
	return send_from_directory('static', 'robots.txt')

# FAVICON
@main.route('/favicon.ico')
def favicon():
	return send_from_directory('static', 'favicon.ico')

# HELP DOCS
@main.route('/help/<string:topic>')
def help(topic):
	try:
		return render_template(f'help/{topic}.html', title='help / '+topic)
	except TemplateNotFound:
		abort(404)

# SEARCH PAGE
@main.route('/search', methods=['GET', 'POST'])
def search():
	page = request.args.get('p', 1, type=int)
	form = SearchForm()
	if form.validate_on_submit():
		current_user.last_search = json.dumps({'wants': form.wanted.data, 'has': form.giving.data, 'sortby': form.sortby.data})
		db.session.commit()

		result = getSearchResults(form, page)
		return redirect(url_for('main.search', w=form.wanted.data, g=form.giving.data, s=form.sortby.data)), 302
	if request.method == 'GET' and current_user.is_authenticated and current_user.last_search:
		lastSearch = json.loads(current_user.last_search)
		form.wanted.data = lastSearch['wants']
		form.giving.data = lastSearch['has']
		form.sortby.data = lastSearch['sortby']
	if ('w' in request.args) and ('g' in request.args) and ('s' in request.args):
		form.wanted.data = request.args.get('w', 'BTC', type=str)
		form.giving.data = request.args.get('g', 'USD', type=str)
		form.sortby.data = request.args.get('s', 'Newest', type=str)
		result = getSearchResults(form, page)
		return render_template('search.html', title='Search Results', form=form, legend='Search', search=True, posts=result, description=f'crytter search results for {form.wanted.data} offers which take {form.giving.data}, sorted by {form.sortby.data}')


	return render_template('search.html', title='Search', form=form, legend='Search', search=False, description=f'Search all of crytter.org\'s offers! Peer-to-peer multicurrency trading network.')

# advertise inquiry info
@main.route('/advertise')
def store():
	return render_template('advertise.html', description=f'Advertise on crytter.org, the leading peer-to-peer currency trading network!', title='Advetise Offers')

# USER MANAGEMENT
@main.route('/manage', methods=['GET', 'POST'])
def admin():
	if not current_user.is_authenticated or current_user.permission_level < 3:
		abort(404)
	badgeform = AssignBadgeForm()
	revokebadgeform = RevokeBadgeForm()
	permform = PermissionsForm()
	emailform = ChangeEmailForm()
	stickyform = StickyPostForm()
	delform = DeleteUserForm()

	isAdmin = False
	if current_user.permission_level == 5: isAdmin = True;

	page = request.args.get('page', 1, type=int)
	users = User.query.order_by(User.date_joined.desc()).paginate(page=page, per_page=20)

	if badgeform.validate_on_submit():
		user = User.query.filter_by(username=badgeform.user.data).first()
		if user:
			badge = Badge(user_id=user.id, name=badgeform.badge_name.data, html=badgeform.badge_html.data)
			db.session.add(badge)
			db.session.commit()
			flash(f'Succesfully assigned "{badgeform.badge_name.data}" badge to user "{badgeform.user.data}".', 'success')
		else:
			flash(f'Could not find user "{badgeform.user.data}".', 'danger')

	elif revokebadgeform.validate_on_submit():
		user = User.query.filter_by(username=revokebadgeform.user.data).first()
		if user: badge = Badge.query.filter_by(user_id=user.id, name=revokebadgeform.badge_name.data).first();
		if user and badge:
			db.session.delete(badge)
			db.session.commit()
			flash(f'Succesfully revoked "{revokebadgeform.badge_name.data}" badge from user "{revokebadgeform.user.data}".', 'success')
		else:
			flash(f'Could not find user "{revokebadgeform.user.data}" with badge "{revokebadgeform.badge_name.data}".', 'danger')

	elif permform.validate_on_submit():
		user = User.query.filter_by(username=permform.user.data).first()
		formlevel = int(permform.level.data)
		if user and user != current_user:
			if isAdmin == False and formlevel >= current_user.permission_level:
				flash('You cannot set other\'s permission levels to values greater than or equal to your own.', 'danger')
			else:
				user.permission_level = formlevel
				db.session.commit()
				flash(f'Succesfully set "{permform.user.data}"\'s permission level to {formlevel}.', 'success')
		elif user == current_user: flash('You cannot manage your own permissions.', 'danger');
		else:
			flash(f'Could not find user "{permform.user.data}".', 'danger')

	elif emailform.validate_on_submit():
		user = User.query.filter_by(email=emailform.user.data).first()
		if not user: user = User.query.filter_by(username=emailform.user.data).first();
		if user:
			if user.id == current_user.id:
				flash(f'To change your own email, please visit the profile page.', 'danger')
			elif user.permission_level >= current_user.permission_level and isAdmin == False:
				flash(f'You cannot change the email of a user with a permission level greater than or equal to yours.', 'danger')
			else:
				user.email = emailform.new_email.data
				db.session.commit()
				flash(f'Changed email for user "{emailform.user.data}".', 'success')
		else:
			flash(f'Could not find user with email/username "{emailform.user.data}".', 'danger')
	
	elif stickyform.validate_on_submit():
		post = Post.query.get(stickyform.post_id.data)
		if post:
			post.sticky = (not post.sticky)
			db.session.commit()
			flash(f'Set "{post.title}" ({post.id})\'s stickiness to {post.sticky}', 'success')
		else:
			flash(f'Unable to find post with ID {stickyform.post_id.data}', 'danger')

	elif delform.validate_on_submit():
		if isAdmin:
			user = User.query.filter_by(username=delform.username.data).first()
			if user:
				posts = Post.query.filter_by(author=user).all()
				ratings = Rating.query.filter_by(rater=user).all()
				badges = Badge.query.filter_by(bearer=user).all()
				receivedRatings = Rating.query.filter_by(ratee=user).all()
				comments = Comment.query.filter_by(author=user).all()
				alerts = Alert.query.filter_by(user_id=user).all()
				alertsFrom = Alert.query.filter_by(from_user=user.id).all()
				for post in posts:
					postComms = Comment.query.filter_by(assoc_post=post)
					for comment in postComms:
						db.session.delete(comment)
					db.session.delete(post)
				for rate in ratings:
					db.session.delete(rate)
				for rate in receivedRatings:
					db.session.delete(rate)
				for comment in comments:
					db.session.delete(comment)
				for badge in badges:
					db.session.delete(badge)
				for alert in alerts:
					db.session.delete(alert)
				for alert in alertsFrom:
					db.session.delete(alert)

				db.session.delete(user)
				db.session.commit()
				flash(f'User "{delform.username.data}" and all related info purged', 'success')
			else:
				flash(f'User "{delform.username.data}" does not exist.', 'danger')
		else:
			flash('You lack the required permissions to purge users', 'danger')


	if request.method == 'POST': return redirect(url_for('main.admin'))
	return render_template('admin.html', title='admin', users=users, badgeform=badgeform, revokebadgeform=revokebadgeform, permform=permform, emailform=emailform, stickyform=stickyform, delform=delform)
