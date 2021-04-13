import re
import secrets
from flask import url_for, current_app
from flask_mail import Message
from crytter import mail

# FUNCTION TO SEND RESET PASSWORD EMAIL
def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Reset Password Request for irony.club', sender='reset@irony.club', recipients=[user.email])
	msg.body = f'''
To reset your password, visit {url_for('users.resetPassword', token=token, _external=True)}

If you did not request a password reset then simply ignore this email and no changes will be made.
'''
	mail.send(msg)

# Ensures a user has the permissions to log in.
def verifyPerms(user):
	if user.permission_level >= 0:
		return True
	else:
		return False

# Get the HTML userbar for a user's rating.
def rateToHTML(rating):
	ratingToBar = {
		-1: '<a class="mr-1 btn btn-danger btn-xs">Disliked</a>',
		20: '<a class="mr-1 btn btn-secondary btn-xs">New User</a>',
		40: '<a class="mr-1 btn btn-light btn-xs" style="color: #000000;">Dealer</a>',
		60: '<a class="mr-1 btn btn-merchant btn-xs">Merchant</a>',
		80: '<a class="mr-1 btn btn-orange btn-xs">Investor</a>',
		100: '<a class="mr-1 btn btn-tycoon btn-xs ml-2">Tycoon</a>'
		}

	if rating < 0: return ratingToBar[-1]
	if rating > 100: return ratingToBar[100]

	rating = (rating + 19) // 20 * 20

	try:
		return ratingToBar[rating]
	except KeyError:
		return ratingToBar[20]