from flask import Blueprint, render_template
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, NumberRange
import requests
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor , CKEditorField
import datetime
import re

books = Blueprint('books', __name__, static_folder='static',template_folder='templates')





class BooksForm(FlaskForm):
	search = StringField('Search for a Book', validators=[DataRequired()],render_kw={"placeholder": "Search for a Book"})
	options = SelectField('Choose Post Type:', choices=[('Book Review', 'Book Review'),
		('Moive Review', 'Movie Review'),
		('Writing', 'Writing')])
	title = StringField('Title - تایتڵ', validators=[DataRequired()], render_kw={"placeholder": "Book's Title"})
	author = StringField('Author - ناوی نوسەر')
	post_img = StringField('Img_url - لینکی وێنە')
	rating = FloatField('Rating (example 4.3)', validators=[ NumberRange(min=1.0, max=5.0)])
	body = CKEditorField('Body',validators=[DataRequired()])
	post_type = StringField('Post Type', validators=[DataRequired()])
	subtitle = StringField('Subtitle - کورتە' )
	first_published = StringField('Published year')
	cover_img = StringField("Cover Img")
	submit = SubmitField('Submit')
	recaptcha  = RecaptchaField()




@books.route('/reviews', methods=['GET', 'POST'])
@login_required
def reviews():
	from models import BookReview
	route = 'books_reviews'
	
	reviews = reversed(BookReview.query.order_by(BookReview.id).all())
	return render_template('books/books_reviews.html',route=route,reviews=reviews, user=current_user.is_authenticated)





@books.route('/new_review', methods=['GET','POST'])
@login_required
def new_review():
	from models import Movie, Users, BookReview
	from init import db
	route = 'new_review'
	form = BooksForm()
	user = db.session.query(Users).filter_by(id=current_user.id).first()

	if 'submit1' in request.form:

		if request.form.get('body') == '':
			flash("Please fill in all the Fields, Except img url it's optional!",'error')

		elif len(request.form.get('body')) <= 20 or len(form.subtitle.data) <= 10:
			flash("Your subtitle or body's text should be longer!",'error')


		elif type(form.rating.data) != float:
			flash('Your Rating Should be in float! (example 8.3)','error')

		elif form.rating.data < 2.0 or form.rating.data > 10.0:
			flash('Your Rating should be higher than 2.0 and lower than 10.0','error')



		else:

			variable = {'q': f'{form.title.data} {form.author.data}','limit': 1}
			respons = requests.get("https://openlibrary.org/search.json",params=variable)
			data = respons.json()
			book = data['docs'][0]

			if book.get('first_sentence'):
				first_sentence = book['first_sentence']
			else:
				first_sentence = 'Unavailable'

			if book.get('ratings_average'):
				ratings_average = book['ratings_average']

			else:
				ratings_average = 0.0

			title = form.title.data
			author_name = form.author.data
			rating = form.rating.data

			first_published = form.first_published.data

			subtitle = form.subtitle.data
			post_img = form.post_img.data
			post_type = form.options.data
			current_date = datetime.datetime.now()
			date = current_date.strftime("%Y %m %d %H:%M")
			body = request.form.get('body')
			cover_img = form.cover_img.data

			new_review = BookReview(title=title,subtitle=subtitle,post_type=post_type,
				date=date,body=body, post_img=post_img,first_published=first_published, cover_img=cover_img,my_rating=rating, writer=author_name,author_id=current_user.id
				,first_sentence=first_sentence,ratings_average=ratings_average)
			user.num_posts = user.num_posts + 1
			db.session.add(new_review)
			db.session.commit()

			return redirect(url_for('home'))

	if 'submit2' in request.form:
		variable = {
		'q':form.title.data,
		'limit': 10
		}
		respons = requests.get("https://openlibrary.org/search.json",params=variable)
		data = respons.json()
		books = data['docs']
		route = 'new_review_book'

		return render_template('books/new_book_review.html', form=form, route=route, books=books)
	

	return render_template('books/new_book_review.html',route=route, form=form, user=current_user.is_authenticated)


@books.route('/new_review_book/<index>', methods=['GET','POST'])
@login_required
def new_review_book(index):
	from init import strip_leading_slash, db
	from models import BookReview, Users
	route = 'new_review_book'
	user = db.session.query(Users).filter_by(id=current_user.id).first()
	book_title, author_name = index.split('_')
	cleaned_name = author_name.strip("[]").strip("'")
	variable = {
	'q': f'{book_title} {author_name}',
	'limit': 1
	}
	respons = requests.get("https://openlibrary.org/search.json",params=variable)
	data = respons.json()
	book = data['docs'][0]

	if book.get('author_name'):
		author_name = book['author_name'][0]
	else:
		author_name = ''

	if book.get('first_publish_year'):
		first_publish_year = book['first_publish_year']
	else:
		first_publish_year = ''

	if book.get('cover_edtition_key'):
		key = book['cover_edtition_key']
		cover_img = f"https://covers.openlibrary.org/b/olid/{key}-L.jpg"

	elif book.get('cover_i'):
		key = book['cover_i']
		cover_img = f"https://covers.openlibrary.org/b/id/{key}-L.jpg"

	elif book.get('edition_key'):
		key = book['edition_key'][0]
		cover_img = f"https://covers.openlibrary.org/b/olid/{key}-L.jpg"
	else:
		cover_img = ''

	if book.get('first_sentence'):
		first_sentence = book['first_sentence'][0]

	else:
		first_sentence = 'Unavailable'
	if book.get('ratings_average'):
		ratings_average = book['ratings_average']
	else:
		ratings_average = 0.0

	form = BooksForm(title=book['title'],author=author_name,first_published=first_publish_year, cover_img=cover_img)




	if 'submit2' in request.form:
		variable = {
		'q':form.title.data,
		'limit': 10
		}
		respons = requests.get("https://openlibrary.org/search.json",params=variable)
		data = respons.json()
		books = data['docs']
		route = 'new_review_book'

		return render_template('books/new_book_review.html', form=form, route=route, books=books)


	if 'submit1' in request.form:

		if request.form.get('body') == '':
			flash("Please fill in all the Fields, Except img url it's optional!",'error')

		elif len(request.form.get('body')) <= 20 or len(form.subtitle.data) <= 10:
			flash("Your subtitle or body's text should be longer!",'error')


		elif type(form.rating.data) != float:
			flash('Your Rating Should be in float! (example 8.3)','error')

		elif form.rating.data < 2.0 or form.rating.data > 10.0:
			flash('Your Rating should be higher than 2.0 and lower than 10.0','error')





		else:
			title = form.title.data
			author_name = form.author.data
			rating = form.rating.data

			first_published = form.first_published.data

			subtitle = form.subtitle.data
			post_img = form.post_img.data
			post_type = form.options.data
			current_date = datetime.datetime.now()
			date = current_date.strftime("%Y %m %d %H:%M")
			body = request.form.get('body')
			cover_img = form.cover_img.data

			new_review = BookReview(title=title,subtitle=subtitle,post_type=post_type,
				date=date,body=body, post_img=post_img,first_published=first_published, cover_img=cover_img,my_rating=rating, writer=author_name,author_id=current_user.id
				,first_sentence=first_sentence,ratings_average=ratings_average) #DB IS NOT IMPORTED!!!
			user.num_posts = user.num_posts + 1 #USER IS NOT IMPORTED!!!!!!
			db.session.add(new_review)
			db.session.commit()

			return redirect(url_for('home'))


	return render_template('books/new_book_review.html',route=route, form=form)





@books.route('books-to-read', methods=['GET','POST'])
def books_to_read():
	from init import db
	from models import Users, BooktoRead
	route = 'book-to-read'

	books =BooktoRead.query.order_by(BooktoRead.id).all()

	if len(books) <= 0:
		error = "There's No Books in the Book-to-Read!"
		

	else:
		error = ""

	books = reversed(books)
	print(error)


	return render_template('books/search.html',error=error,books=books,route=route, user=current_user.is_authenticated)




@books.route('review/<int:id>', methods=['GET','POST'])
def review(id):
	from models import Users, BookReview
	from init import db, is_arabic



	review = db.session.query(BookReview).filter_by(id=id).first()
	route = 'view-review'
	
	is_arabic_body = is_arabic(review.body)
	is_arabic_title = is_arabic(review.title)
	is_arabic_subtitle = is_arabic(review.subtitle)


	is_arabic_text = {
	'body':is_arabic_body,
	'title': is_arabic_title,
	'subtitle': is_arabic_subtitle

	}

	return render_template('books/the_review.html',review=review, is_arabic_text=is_arabic_text)




@books.route('edit_review/<int:id>', methods=['GET','POST'])
def edit_review(id):
	from models import Users, BookReview
	from init import db
	review = db.session.query(BookReview).filter_by(id=id).first()
	route = 'edit_review'

	form = BooksForm(title=review.title, subtitle=review.subtitle, rating=review.my_rating, post_img=review.post_img , cover_img=review.cover_img ,body=review.body, author=review.writer,
		first_published=review.first_published)

	if request.method == 'POST':
		review.title = form.title.data
		review.subtitle = form.subtitle.data
		review.my_rating = form.rating.data
		review.post_img = form.post_img.data
		review.cover_img = form.cover_img.data
		review.body = request.form.get('body')
		review.writer = form.author.data
		review.first_published = form.first_published.data
		db.session.commit()

		return redirect(url_for('books.review', id=id))


	return render_template('books/new_book_review.html',route=route,form=form)


@books.route('/delete/<int:id>', methods=['GET','POST'])
def delete(id):
	from init import db
	from models import BookReview

	the_review = db.session.query(BookReview).filter_by(id=id).first()
	db.session.delete(the_review)
	db.session.commit()
	return redirect(url_for('books.reviews'))




@books.route('/search', methods=['GET','POST'])
def search():
	form = BooksForm()

	if request.method == 'POST':
		variable = {
		'q':form.search.data,
		'limit': 50
		}
		respons = requests.get("https://openlibrary.org/search.json",params=variable)
		data = respons.json()
		data = data['docs']


		books = []
		if not data:
			flash('No books were found!')

		else:
			for i in data:


				if i.get('first_publish_year'):
					if i.get('ratings_average') or i.get('first_sentence'):
						books.append(i)

					else:
						pass

				else:
					pass
		if not books:
			flash('No books were found!')
		return render_template('books/search.html',form=form,books=books, user=current_user.is_authenticated)



	return render_template('books/search.html', form=form, user=current_user.is_authenticated)



@books.route('/the_book/<index>',methods=['GET','POST'])
def the_book(index):
	book_title, author_name, release_date = index.split('_')
	cleaned_name = author_name.strip("[]").strip("'")
	variable = {
	'q': f'{book_title} {author_name}',
	'limit': 25
	}
	the_book = {}
	respons = requests.get("https://openlibrary.org/search.json",params=variable)
	data = respons.json()
	books = data['docs']




	for i in books:
		if i.get('author_name'):
			name = i['author_name']
			name = str(name).strip('[]').strip("'")
		if i.get('first_publish_year'):
			if i.get('ratings_average') or i.get('first_sentence'):
				if i['title'] == book_title and name == cleaned_name and int(i['first_publish_year']) == int(release_date):
					the_book = i

	if the_book.get('ratings_average'):
		rating = the_book['ratings_average']
		rating = float(rating)

	else:
		rating= None


	if the_book.get('cover_edtition_key'):
		key = the_book['cover_edtition_key']
		cover_img = f"https://covers.openlibrary.org/b/olid/{key}-L.jpg"

	elif the_book.get('cover_i'):
		key = the_book['cover_i']
		cover_img = f"https://covers.openlibrary.org/b/id/{key}-L.jpg"

	elif the_book.get('edition_key'):
		key = the_book['edition_key'][0]
		cover_img = f"https://covers.openlibrary.org/b/olid/{key}-L.jpg"
	else:
		cover_img = "\static\pictrues\no-pic-found.jpg"

	return render_template('books/the_book.html', book=the_book, rating=rating, cover_img=cover_img, user=current_user.is_authenticated)


@books.route('/add-to-read/<index>', methods=['GET','POST'])
@login_required
def add_to_read(index):
	from init import db
	from models import BooktoRead, Users
	book_title, author_name, release_date = index.split('_')
	cleaned_name = author_name.strip("[]").strip("'")
	variable = {
	'q': f'{book_title} {author_name}',
	'limit': 25
	}
	the_book = {}
	respons = requests.get("https://openlibrary.org/search.json",params=variable)
	data = respons.json()
	books = data['docs']

	for i in books:
		if i.get('author_name'):
			name = i['author_name']
			name = str(name).strip('[]').strip("'")
		if i.get('first_publish_year'):
			if i.get('ratings_average') or i.get('first_sentence'):
				if i['title'] == book_title and name == cleaned_name and int(i['first_publish_year']) == int(release_date):
					the_book = i

	if the_book.get('ratings_average'):
		rating = the_book['ratings_average']
		rating = float(rating)

	else:
		rating= None


	if the_book.get('cover_edtition_key'):
		key = the_book['cover_edtition_key']
		cover_img = f"https://covers.openlibrary.org/b/olid/{key}-L.jpg"

	elif the_book.get('cover_i'):
		key = the_book['cover_i']
		cover_img = f"https://covers.openlibrary.org/b/id/{key}-L.jpg"

	elif the_book.get('edition_key'):
		key = the_book['edition_key'][0]
		cover_img = f"https://covers.openlibrary.org/b/olid/{key}-L.jpg"
	else:
		cover_img = "\static\pictrues\no-pic-found.jpg"

	title = the_book['title']

	book_author = the_book['author_name']
	writer = str(book_author).strip('[]').strip("'")

	if the_book.get('first_sentence'):
		first_sentence = the_book['first_sentence']
		first_sentence = str(first_sentence).strip('[]').strip("'")

	else:
		first_sentence = 'There is no overview or frist sentence for this book'

	first_published = the_book['first_publish_year']



	the_movie= BooktoRead(title=title,rating=rating,cover_img=cover_img,first_sentence=first_sentence,writer=writer,first_published=first_published,author_id=current_user.id)
	db.session.add(the_movie)
	db.session.commit()

	flash("The book Was added, Check Books > Books-to-Read", 'success')
	return redirect(url_for('books.search'))






@books.route('/to-read-book/<int:id>')
def to_read_book(id):
	from init import db
	from models import BooktoRead
	the_book = db.session.query(BooktoRead).filter_by(id=id).first()
	route = 'book-to-read'
	return render_template('books/the_book.html', book=the_book, route=route, user=current_user.is_authenticated)


@books.route('/i-have-read-it/<int:id>', methods=['GET','POST'])
def i_have_read_it(id):
	from init import db
	from models import BooktoRead

	the_book = db.session.query(BooktoRead).filter_by(id=id).first()
	db.session.delete(the_book)
	db.session.commit()
	return redirect(url_for('books.books_to_read'))



