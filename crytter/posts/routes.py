from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from crytter import db
from crytter.models import Post, Comment, Alert
from crytter.posts.forms import PostForm, CommentForm

posts = Blueprint('posts', __name__)

# MAKE NEW POST PAGE
@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=f'I want {form.howMuchWanted.data} {form.wanted.data}, I\'ll give {form.howMuchGiving.data} {form.giving.data}', content=form.content.data, author=current_user, wanted=form.wanted.data, amountWanted=form.howMuchWanted.data, giving=form.giving.data, amountGiving=form.howMuchGiving.data)
		db.session.add(post)
		db.session.commit()
		flash(f'Posted your offer.', 'success')
		return redirect(url_for('posts.post', post_id=post.id))
	return render_template('newpost.html', title='New Offer', form=form, legend='New Offer', submit='Post Offer')

# VIEW EXISTING POST PAGE
@posts.route('/post/<int:post_id>', methods=["GET",'POST'])
def post(post_id):
	post = Post.query.get_or_404(post_id)
	page = request.args.get('page', 1, type=int)
	comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_commented.desc()).paginate(page=page, per_page=5)
	form = CommentForm()
	if form.validate_on_submit():
		if not current_user.is_authenticated: abort(403)
		comment = Comment(content=form.content.data, author=current_user, assoc_post=post)
		alert = Alert(assoc_user=post.author, type='comment', from_user=current_user.id, post_id=post.id)
		db.session.add(comment)
		db.session.add(alert)
		db.session.commit()
		flash(f'Commented on "{post.title}".', 'success')
		return redirect(url_for('posts.post', post_id=post.id))
	return render_template('post.html', title=post.title, post=post, comments=comments, form=form, submit='comment')

# EDIT EXISTING POST PAGE
@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = f'I want {form.howMuchWanted.data} {form.wanted.data}, I\'ll give {form.howMuchGiving.data} {form.giving.data}'
		post.content = form.content.data
		post.wanted = form.wanted.data
		post.giving = form.giving.data
		post.amountWanted = form.howMuchWanted.data
		post.amountGiving = form.howMuchGiving.data
		db.session.commit()
		flash('Post updated.', 'success')
		return redirect(url_for('posts.post', post_id=post.id))
	elif request.method == 'GET':
		form.wanted.data = post.wanted
		form.giving.data = post.giving
		form.howMuchWanted.data = post.amountWanted
		form.howMuchGiving.data = post.amountGiving
		form.content.data = post.content
	return render_template('newpost.html', title='Edit Offer', form=form, legend='Edit Offer', submit='Update Offer')

# DELETE EXISTING POST PAGE
@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	commentsforpost = Comment.query.filter_by(post_id=post_id).all()
	for comment in commentsforpost:
		db.session.delete(comment)
	db.session.delete(post)
	db.session.commit()
	flash('Offer deleted.', 'success')
	return redirect(url_for('main.home'))

# DELETE COMMENT
@posts.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	if comment.author != current_user:
		abort(403)
	db.session.delete(comment)
	db.session.commit()
	flash('Comment deleted.', 'success')
	return redirect(url_for('posts.post', post_id=request.args.get('returnid')))