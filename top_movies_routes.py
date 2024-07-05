from flask import Blueprint, render_template
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


second = Blueprint('second', __name__, static_folder='static',template_folder='templates')


headers = {
	'accept':'application/json',
	'Authorization': 'Shapol eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0YmRmNDRjYzZlMzFiODhhY2RmZjI2MTFhM2VjMTE3ZCIsInN1YiI6IjY1YjZjZDI4NWUxNGU1MDE0N2FjZDkzMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.fvuB7z_-W5qVzH1mLkcLWjeCFXgpGm62vk9fpeHOmQ4'
}



class MyForm(FlaskForm):
    rating = StringField('Rating', validators=[DataRequired()])
    ranking = StringField('Rank', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    add = StringField('Search Movie', validators=[DataRequired()])



@second.route('/')
def top_movies():
	from models import Movie
	from init import db

	
	all_movie = db.session.query(Movie).order_by(Movie.rating).all()
	for i in range(len(all_movie)):
		all_movie[i].ranking = len(all_movie) - i
		db.session.commit()
	all_movie = reversed(all_movie)
	route = 'top_movies'
	return render_template('top_movies_templates/top_movies_index.html',movies=all_movie, route=route,user=current_user.is_authenticated)


@second.route('/add', methods=['POST','GET'])
def selectmovie():
	form = MyForm()

	movies = []
	if request.method == 'POST':
		movie_name = request.form.get('add')
		variable = {
		'query': movie_name,
		'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'
		}

		respons = requests.get('https://api.themoviedb.org/3/search/movie', headers=headers, params=variable)
		data = respons.json()
		movies = data['results']

		return render_template('top_movies_templates/add.html',form=form,movies=movies)

	return render_template('top_movies_templates/add.html', form=form)



@second.route('/addmovie/<int:id>')
def addmovie(id):
	from init import db
	from models import Movie
	
	variable = {'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'}
	respons = requests.get(f'https://api.themoviedb.org/3/movie/{id}?append_to_response=shapa&language=en-US'
		,headers=headers, params=variable)
	data = respons.json()
	title = data['title']
	img_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
	year = data['release_date'].split("-")[0]
	description = data['overview']
	new_movie = Movie(title=title,img_url=img_url,year=year,description=description,ranking='None',review='...',rating=0.0)
	db.session.add(new_movie)
	db.session.commit()
	the_movie = Movie.query.filter_by(title=title).first()
	movie_title = the_movie.title

	return redirect(url_for('second.edit',index=movie_title))




@second.route('/edit/<index>', methods=['GET','POST'])
def edit(index):
	from init import db
	from models import Movie
	the_movie = Movie.query.filter_by(title=index).first()
	form = MyForm()
	
	if request.method == 'POST':
		rating = request.form.get('rating')
		review = request.form.get('review')

		the_movie.rating = rating
		the_movie.review = review
		db.session.commit()

		return redirect(url_for('second.top_movies'))

	return render_template('top_movies_templates/edit.html',movie=the_movie,form=form)





@second.route('/whole_review/<title>' ,methods=['GET','POST'])
def whole_review(title):
	from init import db
	from models import MovieReviews

	the_movie = db.session.query(MovieReviews).filter_by(title=title).first()

	if the_movie:
		return redirect(url_for('third.the_review', id=the_movie.id))

	else:
		flash('Sorry review for that movie was not found!','error')

		return redirect(url_for('second.top_movies'))









@second.route('/<int:id>', methods=['GET','POST'])
def delete(id):
	from init import db 
	from models import Movie

	the_movie = Movie.query.filter_by(id=id).first()
	if request.method == 'GET':
		db.session.delete(the_movie)
		db.session.commit()
		return redirect(url_for('second.top_movies'))

	return render_template('index.html')






