from flask import Blueprint, render_template
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, FloatField, DecimalField
from wtforms.validators import DataRequired, NumberRange, InputRequired, ValidationError
import requests
from flask_ckeditor import CKEditor , CKEditorField
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import datetime
from jinja2 import Environment
third = Blueprint('third', __name__, static_folder='static',template_folder='templates')


headers = {
	'accept':'application/json',
	'Authorization': 'Shapol eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0YmRmNDRjYzZlMzFiODhhY2RmZjI2MTFhM2VjMTE3ZCIsInN1YiI6IjY1YjZjZDI4NWUxNGU1MDE0N2FjZDkzMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.fvuB7z_-W5qVzH1mLkcLWjeCFXgpGm62vk9fpeHOmQ4'
}



def detect_language(text):
	if any(char >= '\u0600' and char <= '\u06FF' for char in text):
		return 'arabic'

	else:

		return 'english'
env = Environment()
env.filters['detect_language'] = detect_language




class MyForm(FlaskForm):
	options = SelectField('Choose Post Type:', choices=[
		('Movie Review', 'Movie Review'),
		('Writing', 'Writing'),
		('Book Review','Book Review')])
	title = StringField('Title - تایتڵ', validators=[DataRequired()], render_kw={"placeholder": "Search For Movie's Name"})
	author = StringField('Author - ناوی نوسەر')
	post_img = StringField("Post Img")
	rating = FloatField('Rating (example 8.3)', validators=[ NumberRange(min=1.0, max=10.0)])
	body = CKEditorField('Body',validators=[DataRequired()])
	post_type = StringField('Post Type', validators=[DataRequired()])
	subtitle = StringField('Subtitle - کورتە' )
	cover_img = StringField("Cover Img")
	submit = SubmitField('Submit')


@third.route('/',methods=['GET', 'POST'])
@login_required
def reviews():
	from models import MovieReviews, Users, db
	route = 'movies_reviews'

	movies = reversed(MovieReviews.query.order_by(MovieReviews.id).all())

	return render_template('movie_reviews/reviews.html',route=route, movies=movies, detect_language=detect_language, user=current_user.is_authenticated)




@third.route('/new_review', methods=['GET', 'POST'])
@login_required
def new_review():
	form = MyForm()
	route = 'new_review'

	if 'submit1' in request.form:
		from models import MovieReviews, Users, db
		user = db.session.query(Users).filter_by(id=current_user.id).first()

		try:
			movie_name = request.form.get('title')
			only_name = movie_name.split('(')[0]
			variable = {
			'query': only_name,
			'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'
			}
			respons = requests.get('https://api.themoviedb.org/3/search/movie', headers=headers, params=variable)
			data= respons.json()
			data = data['results'][0]
			overview = data['overview']
			release_date = data['release_date']
			vote_average = data['vote_average']
		except IndexError:
			overview = 'Unavailable'
			release_date = 'Unavailable'
			vote_average = 0.0



		if request.form.get('body') == '' or form.subtitle.data == '' or form.rating.data == None:
			flash("Please fill in the fields, Except img url it's optinal!",'error')
			

		elif len(request.form.get('body')) <= 20 or len(form.subtitle.data) <= 10:
			flash("Your subtitle or body's text should be longer!",'error')

		elif type(form.rating.data) != float:
		    flash('Your Rating Should be in float! (example 8.3)','error')

		elif form.rating.data < 2.0 or form.rating.data > 10.0:
			flash('Your Rating should be higher than 2.0 and lower than 10.0','error')

		else:
			title = request.form.get('title')
			post_img = form.post_img.data
			current_date = datetime.datetime.now()
			date = current_date.strftime("%Y %m %d %H:%M")
			body = request.form.get('body')
			rating = form.rating.data
			author = current_user.id
			subtitle= form.subtitle.data
			post_type = form.options.data
			cover_img = form.cover_img.data
			new_review = MovieReviews(title=title,date=date,my_rating=rating,body=body,
			post_img=post_img,post_type=post_type, author_id=author, subtitle=subtitle, cover_img=cover_img,
			overview=overview, vote_average=vote_average,release_date=release_date)
			user.num_posts = user.num_posts + 1
			db.session.add(new_review)
			db.session.commit()
			return redirect(url_for('third.reviews'))

	if 'submit2' in request.form:
		movie_name = request.form.get('title')
		variable = {
		'query': movie_name,
		'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'
		}
		respons = requests.get('https://api.themoviedb.org/3/search/movie', headers=headers, params=variable)
		data= respons.json()
		movies = data['results']
		route = 'new_movie_review'
		

		return render_template('movie_reviews/new_review.html', movies=movies, form=form, route=route, user=current_user.is_authenticated)


	

	

	return render_template('movie_reviews/new_review.html', form=form, route=route, user=current_user.is_authenticated)





@third.route('new_review_movie/<int:id>', methods=['GET', 'POST'])
@login_required
def new_review_movie(id):
	route = 'new_review_movie'

	variable = {'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'}
	respons = requests.get(f'https://api.themoviedb.org/3/movie/{id}?append_to_response=shapa&language=en-US'
		,headers=headers, params=variable)
	data = respons.json()
	year = data['release_date'].split("-")[0]
	title = f"{data['title']} ({year})"
	cover_img = f'https://image.tmdb.org/t/p/original{data["poster_path"]}'
	overview = data['overview']
	release_date = data['release_date']
	vote_average = data['vote_average']
	if data['backdrop_path'] == None :
		if data['poster_path'] == None:
			img_url = 'https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg'
		else:

			img_url = f'https://image.tmdb.org/t/p/original{data["poster_path"]}'



	else: 
		img_url = f"https://image.tmdb.org/t/p/original{data['backdrop_path']}"
 
	
	description = data['overview']

	form = MyForm(title=title,post_img=img_url,cover_img=cover_img)




	if 'submit2' in request.form:
		
		movie_name = request.form.get('title')
		variable = {
		'query': movie_name,
		'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'
		}
		respons = requests.get('https://api.themoviedb.org/3/search/movie', headers=headers, params=variable)
		data= respons.json()
		movies = data['results']

		return render_template('movie_reviews/new_review.html', movies=movies, form=form, route=route, user=current_user.is_authenticated)


	if 'submit1' in request.form:
		from models import MovieReviews, Users, db
		user = db.session.query(Users).filter_by(id=current_user.id).first()
		

		if request.form.get('body') == '' or form.subtitle.data == '' or form.rating.data == None:
			flash("Please fill in the fields, Except img url it's optinal!",'error')
			

		elif len(request.form.get('body')) <= 20 or len(form.subtitle.data) <= 10:
			flash("Your subtitle or body's text should be longer!",'error')

		elif type(form.rating.data) != float:
		    flash('Your Rating Should be in float! (example 8.3)','error')

		elif form.rating.data < 2.0 or form.rating.data > 10.0:
			flash('Your Rating should be higher than 2.0 and lower than 10.0','error')

		else:
			title = request.form.get('title')
			post_img = form.post_img.data
			current_date = datetime.datetime.now()
			date = current_date.strftime("%Y %m %d %H:%M")
			body = request.form.get('body')
			rating = form.rating.data
			author = current_user.id
			subtitle= form.subtitle.data
			post_type = form.options.data
			cover_img = form.cover_img.data
			new_review = MovieReviews(title=title,date=date,my_rating=rating,body=body,
			post_img=post_img,post_type=post_type, author_id=author, subtitle=subtitle, cover_img=cover_img,
			overview=overview, vote_average=vote_average,release_date=release_date)
			user.num_posts = user.num_posts + 1
			db.session.add(new_review)
			db.session.commit()
			return redirect(url_for('third.reviews'))


	return render_template('movie_reviews/new_review.html', post_img=img_url,form=form,route=route, user=current_user.is_authenticated)
	


@third.route('/review/<int:id>', methods=['GET','POST'])
@login_required
def the_review(id):
	from models import MovieReviews, Users, db
	from init import db, is_arabic
	review = db.session.query(MovieReviews).filter_by(id=id).first()
	route = 'view-review'

	is_arabic_body = is_arabic(review.body)
	is_arabic_title = is_arabic(review.title)
	is_arabic_subtitle = is_arabic(review.subtitle)


	is_arabic_text = {
	'body':is_arabic_body,
	'title': is_arabic_title,
	'subtitle': is_arabic_subtitle

	}



	return render_template('movie_reviews/the_review.html', review=review, is_arabic_text=is_arabic_text, user=current_user.is_authenticated, route=route)





@third.route('/edit_review/<int:id>', methods=['GET','POST'])
def edit_review(id):
	from models import MovieReviews, Users, db
	review = db.session.query(MovieReviews).filter_by(id=id).first()
	form = MyForm(title=review.title, subtitle=review.subtitle, rating=review.my_rating, post_img=review.post_img,cover_img=review.cover_img ,body=review.body)
	route = 'edit_review'

	if request.method == 'POST':
		review.title = form.title.data
		review.subtitle = form.subtitle.data
		review.my_rating = form.rating.data
		review.post_img = form.post_img.data
		review.cover_img = form.cover_img.data
		review.body = request.form.get('body')
		db.session.commit()

		return redirect(url_for('third.the_review', id=id))





	return render_template('movie_reviews/new_review.html', form=form, route=route, review=review)








@third.route('/delete/<int:id>', methods=['GET','POST'])
@login_required
def review_delete(id):
	from models import db, MovieReviews, Users
	user = db.session.query(Users).filter_by(id=current_user.id).first()

	the_review = db.session.query(MovieReviews).filter_by(id=id).first()

	db.session.delete(the_review)
	db.session.commit()

	return redirect(url_for('home'))