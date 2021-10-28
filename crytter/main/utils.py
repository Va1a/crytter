from crytter.models import User, Post

def getSearchResults(form, page):
	if form.sortby.data == 'Newest':
		result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.date_posted.desc()).paginate(page=page, per_page=5)
	elif form.sortby.data == 'Oldest':
		result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.date_posted.asc()).paginate(page=page, per_page=5)
	elif form.sortby.data == 'Offeror Reputability':
		result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).join(User).order_by(Post.sticky.desc(), User.rating.desc()).paginate(page=page, per_page=5)
	elif form.sortby.data == 'Highest Quantity':
		result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.amountGiving.desc()).paginate(page=page, per_page=5)
	elif form.sortby.data == 'Lowest Quantity':
		result = Post.query.filter(Post.giving == form.wanted.data, Post.wanted == form.giving.data).order_by(Post.sticky.desc(), Post.amountGiving.asc()).paginate(page=page, per_page=5)

	return result