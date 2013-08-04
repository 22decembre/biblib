# -*- coding: utf-8 -*-

import flask
from models import Author, Book
from flask.ext.wtf import Form, Field, TextField, BooleanField, DateField, HiddenField, IntegerField, DecimalField, TextAreaField, QuerySelectField, FileField, file_allowed, validators, Required
from werkzeug import secure_filename

def possible_author():
    return Author.query

def possible_book():
	return Book.query
    #return Book.query(filter(Book.authors != author_id))

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class DeleteForm(Form):
	delete = BooleanField('delete', default = False)
    
class BookForm(Form):
	authortodelete = BooleanField('authortodelete', default = False)
	title = TextField('title', [validators.Required()])
	ean = TextField('ean', [validators.optional()])
	isbn = TextField('isbn', [validators.optional()])
	publisher = TextField('publisher', [validators.optional()])
	thickness = DecimalField('thickness', [validators.optional()])
	width = DecimalField('width', [validators.optional()])
	length = DecimalField('length', [validators.optional()])
	mass = DecimalField('mass', [validators.optional()])
	numberofpages = IntegerField('numberofpages', [validators.optional()])
	cover = FileField("cover", [validators.optional()])
	
	# take care ! I place a textarea and a SelectField here but don't use it in the template, cause I want to be able to fill it, whereas I can't with it!
	# this is needed by the view.
	authortoadd = QuerySelectField('authortoadd', query_factory = possible_author,allow_blank=True)
	summary = TextAreaField('biography', [validators.optional()])

class AuthorForm(Form):
	booktodelete = BooleanField('booktodelete', default = False)
	familyname 	= TextField('familyname', [validators.Required()])
	firstname 	= TextField('firstname', [validators.Required()])
	biography 	= TextAreaField('biography', [validators.optional()])
	#dateofbirth 	= DateField('dateofbirth', [validators.optional()])
	placeofbirth 	= TextField('placeofbirth', [validators.optional()])
	nationality 	= TextField('nationality', [validators.optional()])
	website 	= TextField('website', [validators.optional()])
	
	# il faudrait limiter les valeurs à celles qui NE SONT PAS déjà des bouquins de l'auteur X…
	booktoadd = QuerySelectField('booktoadd', query_factory=possible_book,get_label='title',allow_blank=True)
	portrait = FileField('portrait', [validators.optional()])

class SearchForm(Form):
	title = TextField('title')
	ean = TextField('ean')
	isbn = TextField('isbn')
	author = TextField('author')