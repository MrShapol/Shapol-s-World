from flask import Blueprint, render_template, flash
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


fourth = Blueprint('fourth', __name__, static_folder='static',template_folder='templates')


headers = {
	'accept':'application/json',
	'Authorization': 'Shapol eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0YmRmNDRjYzZlMzFiODhhY2RmZjI2MTFhM2VjMTE3ZCIsInN1YiI6IjY1YjZjZDI4NWUxNGU1MDE0N2FjZDkzMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.fvuB7z_-W5qVzH1mLkcLWjeCFXgpGm62vk9fpeHOmQ4'
}



class MyForm(FlaskForm):
    search = StringField('Search for a movie:', validators=[DataRequired()], render_kw={"placeholder": "Search for Movie you want to watch..."})
    submit = SubmitField('Submit')




@fourth.route('/watch-list', methods=['GET', 'POST'])

def watch_list():
	from init import db
	from models import RecommendMovie
	route = 'watch-list'

	movies = RecommendMovie.query.order_by(RecommendMovie.id).all()

	if len(movies) <= 0:
		error = "There's No movies in the Watchlist!"
		

	else:
		error = ""

	movies = reversed(movies)


	return render_template('movie_towatch/search.html', error=error,movies=movies, route=route, user=current_user.is_authenticated)

@fourth.route('/search', methods=['GET','POST'])
def search():
	form = MyForm()

	if request.method == 'POST':
		movie_name = request.form.get('search')
		variable = {
		'query': movie_name,
		'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'}
		respons = requests.get('https://api.themoviedb.org/3/search/movie', headers=headers, params=variable)
		data= respons.json()
		movies = data['results']

		if not movies:
			flash('No movies were found!')


		return render_template('movie_towatch/search.html',form=form, movies=movies, user=current_user.is_authenticated)



	return render_template('movie_towatch/search.html', form=form)





@fourth.route('/the_movie/<int:id>',methods=['GET', 'POST'])
def the_movie(id):

	variable = {'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'}
	respons = requests.get(f'https://api.themoviedb.org/3/movie/{id}?append_to_response=shapa&language=en-US'
		,headers=headers, params=variable)
	data = respons.json()
	the_movie = data
	rating = data['vote_average']
	rating = float(rating)

	return render_template('movie_towatch/the_movie.html',rating=rating, movie=the_movie, user=current_user.is_authenticated)





@fourth.route('/add_watch-list/<int:id>')
@login_required
def add_movie(id):
	from init import db
	from models import RecommendMovie
	
	variable = {'api_key': '4bdf44cc6e31b88acdff2611a3ec117d'}
	respons = requests.get(f'https://api.themoviedb.org/3/movie/{id}?append_to_response=shapa&language=en-US'
		,headers=headers, params=variable)
	data = respons.json()
	title = data['title']

	post_img = data['backdrop_path']
	rating = data['vote_average']
	rating = float(rating)
	cover_img = data["poster_path"]
	relese_date = data['release_date']
	overview = data['overview']

	if not data.get('backdrop_path') and data.get('poster_path'):
		post_img = '#'
		cover_img = '#'


	if not data.get('overview'):
		overview = 'Unavailable'
	movies = RecommendMovie.query.order_by(RecommendMovie.id).all()

	for movie in movies:
		if title == movie.title:
			flash('The Movie is Already in the Watchlist!', 'error')
			return redirect(url_for('fourth.search'))
	
	the_movie= RecommendMovie(title=title,rating=rating,cover_img=cover_img,post_img=post_img,relese_date=relese_date,overview=overview,author_id=current_user.id)
	db.session.add(the_movie)
	db.session.commit()

	flash("The Movie Was added, Check Movies > Watchlist", 'success')
	return redirect(url_for('fourth.search'))





@fourth.route('/movie-watch-list/<int:id>')
def the_movie_watchlist(id):
	from init import db
	from models import RecommendMovie
	the_movie = db.session.query(RecommendMovie).filter_by(id=id).first()
	route = 'watch-list'
	return render_template('movie_towatch/the_movie.html', movie=the_movie, route=route, user=current_user.is_authenticated)



@fourth.route('/delete/<int:id>',methods=['POST','GET'])
def delete(id):
	from init import db
	from models import RecommendMovie
	
	the_movie = db.session.query(RecommendMovie).filter_by(id=id).first()

	db.session.delete(the_movie)
	db.session.commit()

	return redirect(url_for('fourth.watch_list'))