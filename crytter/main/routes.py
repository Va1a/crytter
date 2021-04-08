from flask import render_template, send_from_directory, request, Blueprint, abort, flash, redirect, url_for
from crytter.models import User, Post, Badge
from flask_login import current_user
from crytter.main.forms import SearchForm, AssignBadgeForm, RevokeBadgeForm, PermissionsForm, ChangeEmailForm, StickyPostForm
from crytter import db
import json

main = Blueprint('main', __name__)

# HOME PAGE
@main.route('/posts')
def home():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', posts=posts)

# ABOUT PAGE
@main.route('/about')
def about():
	return render_template('about.html', title='about')

# SEO ROBOTS.TXT
@main.route('/robots.txt')
def robots():
	return send_from_directory('static', 'robots.txt')

# HELP DOCS
@main.route('/help/<string:topic>')
def help(topic):
	return render_template(f'help/{topic}.html', title=topic)

# SEARCH PAGE
@main.route('/search', methods=['GET', 'POST'])
def search():
	page = request.args.get('page', 1, type=int)
	form = SearchForm()
	if form.validate_on_submit():
		current_user.last_search = json.dumps({'wants': form.wanted.data, 'has': form.giving.data, 'sortby': form.sortby.data})
		db.session.commit()

		if form.sortby.data == 'Newest':
			result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.date_posted.desc()).paginate(page=page, per_page=5)
		elif form.sortby.data == 'Oldest':
			result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.date_posted.asc()).paginate(page=page, per_page=5)
		elif form.sortby.data == 'Highest Credibility':
			result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).join(User).order_by(Post.sticky.desc(), User.rating.desc()).paginate(page=page, per_page=5)
		elif form.sortby.data == 'Highest Quantity':
			result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.amountGiving.desc()).paginate(page=page, per_page=5)
		elif form.sortby.data == 'Lowest Quantity':
			result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.amountGiving.asc()).paginate(page=page, per_page=5)
		return render_template('search.html', title='Search Results', form=form, legend='Search', search=True, posts=result)
	if request.method == 'GET' and current_user.is_authenticated and current_user.last_search:
		lastSearch = json.loads(current_user.last_search)
		form.wanted.data = lastSearch['wants']
		form.giving.data = lastSearch['has']
		form.sortby.data = lastSearch['sortby']
	return render_template('search.html', title='search', form=form, legend='Search', search=False)

# TODO: blank page
@main.route('/advertise')
def store():
	return render_template('advertise.html')

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

	if request.method == 'POST': return redirect(url_for('main.admin'))
	return render_template('admin.html', title='admin', users=users, badgeform=badgeform, revokebadgeform=revokebadgeform, permform=permform, emailform=emailform, stickyform=stickyform)
