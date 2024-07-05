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
import datetime
import random
from books import books
from sqlalchemy.ext.declarative import declarative_base
import os
from init import db, app
from models import BlogPost, Users, Movie, MovieReviews, BookReview
import re
from init import is_arabic

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'welcome'



with app.app_context():
	db.create_all()


@login_manager.user_loader
def load_user(user_id):
	return db.session.query(Users).filter_by(id=int(user_id)).first()





    
class MyForm(FlaskForm):
	options = SelectField('Choose Post Type:', choices=[
		('Writing', 'Writing'),
		('Movie Review', 'Movie Review'),
		('Book Review', 'Book Review')])
	title = StringField('Title - تایتڵ', validators=[DataRequired()])
	subtitle = StringField('Subtitle - کورتە',validators=[DataRequired()] )
	post_img = StringField('Img_url - لینکی وێنە')
	author = StringField('Author - ناوی نوسەر')
	body = CKEditorField('Body',validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	password = StringField('Password', validators=[DataRequired()])
	name = StringField('name', validators=[DataRequired()])
	post_type = StringField('Post Type', validators=[DataRequired()])



@app.route('/')
def welcome():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
		

	return render_template('welcome.html')




@app.route('/feed')
@login_required
def home():
	route = 'home'

	all_posts = []
	books_reviews = BookReview.query.order_by(BookReview.id).all()

	blog_posts = BlogPost.query.order_by(BlogPost.id).all()
	movie_reviews = MovieReviews.query.order_by(MovieReviews.id).all()

	for i in blog_posts:
		all_posts.append(i)

	for i in movie_reviews:
		all_posts.append(i)

	for i in books_reviews:
		all_posts.append(i)




	posts = sorted(all_posts, key=lambda x: x.date, reverse=True)

	return render_template('index.html',posts=posts, user=current_user.is_authenticated, route=route)



@app.route('/login',methods=['GET','POST'])
def login():
	form = MyForm()
	error = None
	route = 'login'

	if current_user.is_authenticated:
		return redirect(url_for('home'))

	email = request.form.get('email')
	if request.method == 'POST':
		try:
		    user = db.session.query(Users).filter_by(email=email.lower()).first()
		    password = check_password_hash(user.password,request.form.get('password'))
		    if password:

		    	login_user(user)
		    	return redirect(url_for('home'))
		    else:
		    	error = 'Your Password is Invaild!, Please Try Again!'

		except AttributeError or UnboundLocalError:
			error = 'This Email does not exist, Please Try Again!'		

	return render_template('login.html',form=form, error=error, route=route)

@app.route('/logout',methods=['POST','GET'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('welcome'))


@app.route('/post/<int:index>',methods=['GET', 'POST'])
def the_post(index):
	the_post = db.session.query(BlogPost).filter_by(id=index).first()
	route = 'view-post'

	is_arabic_body = is_arabic(the_post.body)
	is_arabic_title = is_arabic(the_post.title)
	is_arabic_subtitle = is_arabic(the_post.subtitle)


	is_arabic_text = {
	'body':is_arabic_body,
	'title': is_arabic_title,
	'subtitle': is_arabic_subtitle

	}



	return render_template('post.html',post=the_post,is_arabic_text=is_arabic_text, user=current_user.is_authenticated,route=route)



@app.route('/new_post',methods=['POST','GET'])
@login_required
def new_post():
	user = db.session.query(Users).filter_by(id=current_user.id).first()
	
	form = MyForm(author=user.name, post_type='Writing')

	if request.method == 'POST':
		if request.form.get('body') == '':
			flash("Please fill in all the Fields, Except img url it's optional!",'error')
			

		elif len(request.form.get('body')) <= 20 or len(form.subtitle.data) <= 10:
			flash("Your subtitle or body's text should be longer!",'error')



		else:
			title = form.title.data
			subtitle = form.subtitle.data
			post_img = form.post_img.data
			post_type = form.options.data
			current_date = datetime.datetime.now()
			date = current_date.strftime("%Y %m %d %H:%M")
			body = request.form.get('body')
			new_post = BlogPost(title=title,subtitle=subtitle,poster_id=current_user.id, body=body,post_img=post_img,date=date,post_type=post_type)
			user.num_posts = user.num_posts + 1
			db.session.add(new_post)
			db.session.commit()

			return redirect(url_for('posts'))
	route = 'new_post'


	return render_template('newpost.html',form=form,route=route, user=current_user.is_authenticated)



@app.route('/delete/<int:index>')
def delete(index):
	the_post = db.session.query(BlogPost).filter_by(id=index).first()

	user = db.session.query(Users).filter_by(id=current_user.id).first()

	user.num_posts = user.num_posts - 1

	db.session.delete(the_post)
	db.session.commit()

	return redirect(url_for('home'))


@app.route('/edit-post/<int:index>', methods=['POST','GET'])
@login_required
def edit_post(index):
	post = db.session.query(BlogPost).filter_by(id=index).first()
	form = MyForm(
		title=post.title,
    subtitle=post.subtitle,
    post_img=post.post_img,
    body=post.body,post_type=post.post_type)
	if request.method == 'POST':
		post.title = form.title.data
		post.subtitle = form.subtitle.data
		post.post_img = form.post_img.data
		post.body = request.form.get('body')
		db.session.commit()

		return redirect(url_for('the_post',index=index))
	route = 'edit-post'

	return render_template('newpost.html',form=form, route=route, user=current_user.is_authenticated)


@app.route('/about')

def about_blog():
	return render_template('about.html', user=current_user.is_authenticated)


@app.route('/profile')
def profile():
	return render_template('profile.html', user=current_user.is_authenticated)




@app.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
	route = 'writings'

	posts = reversed(BlogPost.query.order_by(BlogPost.id).all())


	return render_template('index.html',route=route, posts=posts, user=current_user.is_authenticated)









@app.route('/register', methods=['GET','POST'])
def register():
	form = MyForm()
	if request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		name = request.form.get('name')
		hashed_pass = generate_password_hash(password=password,method='pbkdf2:sha256',salt_length=8)
		num_posts = 0

		db.session.add(Users(name=name,email=email.lower(),password=hashed_pass,num_posts=num_posts))
		db.session.commit()
		user = db.session.query(Users).filter_by(name=name).first()
		login_user(user)

		return redirect(url_for('home'))
	return render_template('register.html',form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)