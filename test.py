from flask import Blueprint, render_template
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import sys
import codecs
import datetime
from PIL import Image
from io import BytesIO
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


headers = {
	'accept':'application/json',
	'Authorization': 'Shapol eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0YmRmNDRjYzZlMzFiODhhY2RmZjI2MTFhM2VjMTE3ZCIsInN1YiI6IjY1YjZjZDI4NWUxNGU1MDE0N2FjZDkzMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.fvuB7z_-W5qVzH1mLkcLWjeCFXgpGm62vk9fpeHOmQ4'
}







variable = {
'q':"Harry Potter Boxed Set",
'limit': 5
}

descs = []
the_ids = []
respons = requests.get("https://openlibrary.org/search.json",params=variable)
data = respons.json()
books = data['docs']

for i in books:
	print(i['first_publish_year'], i['author_name'], i['ratings_average'])




