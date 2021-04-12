from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp
from crytter.posts.validators import NotEqualTo, cryptoList

class PostForm(FlaskForm):
	wanted = SelectField('Currency you want:', choices=cryptoList, validators=[DataRequired()])
	howMuchWanted = StringField('How much do you want?', validators=[DataRequired(), Regexp(r'^[0-9.]*$', message='Must be a number')])
	giving = SelectField('Currency you are willing to give:', choices=cryptoList, validators=[DataRequired(), NotEqualTo('wanted', message='You cannot give the same currency you want.')])
	howMuchGiving = StringField('How much are you willing to give?', validators=[DataRequired(), Regexp(r'^[0-9.]*$', message='Must be a number')])
	content = TextAreaField('Offer Information', validators=[DataRequired(), Length(max=2000, message='Too long, maximum 2000 characters')])
	recaptcha = RecaptchaField(validators=[Recaptcha(message="Prove you are not a robot.")])
	submit = SubmitField('post')



class CommentForm(FlaskForm):
	content = TextAreaField('Add a Comment', validators=[DataRequired(), Length(min=1, max=1000)])
	submit = SubmitField('comment')