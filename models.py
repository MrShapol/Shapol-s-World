from init import db, app
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField , SelectField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor , CKEditorField
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from jinja2 import Environment
from sqlalchemy.orm import relationship, backref



class BlogPost(db.Model):
	__tablename__ = "blog_posts"
	id = db.Column(db.Integer, primary_key=True)

	author = relationship('Users', back_populates='posts')

	title = db.Column(db.String(250), unique=True, nullable=False)
	subtitle= db.Column(db.String(250), nullable=False)
	date = db.Column(db.String(250), nullable=False)
	body = db.Column(db.Text, nullable=False)
	post_img= db.Column(db.String(250), nullable=True)
	post_type = db.Column(db.String(10), nullable=False)
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)





class Users(UserMixin,db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(30), unique=True)
	password = db.Column(db.String(100))
	num_posts = db.Column(db.Integer, nullable=True)


	posts = db.relationship('BlogPost', back_populates='author')
	top_movie = relationship('Movie', back_populates='author')
	movie_reviews = relationship('MovieReviews', back_populates='author')
	recommend_movie = relationship('RecommendMovie', back_populates='author')
	book_to_read = relationship('BooktoRead', back_populates='author')
	book_review = relationship('BookReview', back_populates='author')


class Movie(db.Model):
	__tablename__ = 'top_movies'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	year = db.Column(db.String(50), nullable=False)
	description = db.Column(db.String(255), nullable=False)
	rating = db.Column(db.Float, nullable=True)
	ranking = db.Column(db.Integer, nullable=True)
	review = db.Column(db.String(50), nullable=True)
	img_url = db.Column(db.String(255), nullable=False)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	author = relationship('Users', back_populates='top_movie')


	def __repr__(self):
		return f'{self.title}'

class MovieReviews(db.Model):
	__tablename__ = 'movie_reviews'
	id = db.Column(db.Integer, primary_key=True)

	title = db.Column(db.String(50), nullable=False)
	date = db.Column(db.String(250), nullable=False)
	my_rating = db.Column(db.Float, nullable=False)
	body = db.Column(db.Text, nullable=False)
	subtitle= db.Column(db.String(250), nullable=False)
	post_img = db.Column(db.String(255), nullable=False)
	cover_img = db.Column(db.String(255), nullable=True)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
	post_type = db.Column(db.String(10), nullable=False)
	author = relationship('Users', back_populates='movie_reviews')

	overview = db.Column(db.Text, nullable=True)
	vote_average = db.Column(db.Float, nullable=True)
	release_date =  db.Column(db.String(20), nullable=True)




class RecommendMovie(db.Model):
	__tablename__ = 'recommend_movie'

	id = db.Column(db.Integer, primary_key=True)
	author = relationship('Users', back_populates='recommend_movie')
	title = db.Column(db.String(50), nullable=False)
	rating = db.Column(db.Float, nullable=True)
	relese_date = db.Column(db.String(50), nullable=False)
	overview = db.Column(db.String(250), nullable=False)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=True)
	post_img = db.Column(db.String(255), nullable=False)
	cover_img = db.Column(db.String(255), nullable=False)




class BooktoRead(db.Model):
	__tablename__ = 'books_to_read'

	id = db.Column(db.Integer, primary_key=True)
	author = relationship('Users', back_populates='book_to_read')
	title = db.Column(db.String(50), nullable=False)
	writer = db.Column(db.String(50), nullable=False)
	first_published = db.Column(db.String(100), nullable=False)
	first_sentence = db.Column(db.String(100), nullable=True)
	rating = db.Column(db.Float, nullable=True)
	cover_img = db.Column(db.String(250), nullable=False)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)


class BookReview(db.Model):
	__tablename__ = 'book_review'

	id = db.Column(db.Integer, primary_key=True)
	author = relationship('Users', back_populates='book_review')
	title = db.Column(db.String(50), nullable=False)
	subtitle = db.Column(db.String(100), nullable=False)
	writer = db.Column(db.String(50), nullable=False)
	post_type = db.Column(db.String(50), nullable=False)
	date = db.Column(db.String(50), nullable=False)
	body = db.Column(db.Text, nullable=False)
	post_img = db.Column(db.String(250), nullable=False)
	cover_img = db.Column(db.String(255), nullable=True)
	author_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
	first_published = db.Column(db.String(50), nullable=False)
	my_rating = db.Column(db.Float, nullable=False)

	first_sentence = db.Column(db.Text, nullable=True)
	ratings_average = db.Column(db.Float, nullable=True)

