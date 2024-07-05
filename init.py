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
from top_movies_routes import second
from movie_review import third
from recommend_movie import fourth
import random
from books import books
from sqlalchemy.ext.declarative import declarative_base
import os
import re

app = Flask(__name__)



app.register_blueprint(third, url_prefix='/movies/reviews')
app.register_blueprint(second, url_prefix='/movies/top_movies')
app.register_blueprint(fourth, url_prefix='/movies/')
app.register_blueprint(books, url_prefix='/books')



app.config['SECRET_KEY'] = 'mykey'
app.config['CKEDITOR_PKG_TYPE'] = 'full'

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'example.db')}"
#app.config['SQLALCHEMY_BINDS'] = {
 #   'second_db': 'sqlite:///users.db'
#}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app,db)

ckeditor = CKEditor(app)


@app.template_filter('strip_leading_slash')
def strip_leading_slash(s):
    return s.lstrip('/works/')

app.jinja_env.filters['strip_leading_slash'] = strip_leading_slash




def is_arabic(text):
    arabic_detect = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_detect.search(text))

app.jinja_env.filters['is_arabic'] = is_arabic















Bootstrap(app)