# -*- coding: utf-8 -*-

import flask
from flask.ext.wtf import Form, TextField, BooleanField, DateField, IntegerField, DecimalField, TextAreaField, SelectField, FileField, file_allowed, validators, Required
from flaskext.uploads import UploadSet, IMAGES
from werkzeug import secure_filename

import collections  
books = collections.namedtuple('books', 'id, title')
#for bk in map(books._make, Book.query.with_entities(Book.id,Book.title).all()):

covers = UploadSet('covers', IMAGES)
photos = UploadSet('photos', IMAGES)

def possible_book():
    return Book.query.with_entities(Book.id,Book.title).all()

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class BookForm(Form):
	title = TextField('title', [validators.Required()])
	ean = TextField('ean', [validators.optional()])
	isbn = TextField('isbn', [validators.optional()])
	publisher = TextField('publisher', [validators.optional()])
	thickness = DecimalField('thickness', [validators.optional()])
	width = DecimalField('width', [validators.optional()])
	length = DecimalField('length', [validators.optional()])
	mass = DecimalField('mass', [validators.optional()])
	numberofpages = IntegerField('numberofpages', [validators.optional()])
	cover = FileField("cover", [validators.optional(),file_allowed(covers, "Images only!")])
	
	# take care ! I place a textarea and a SelectField here but don't use it in the template, cause I want to be able to fill it, whereas I can't with it!
	# this is needed by the view.
	authorlist = SelectField('author_list', [validators.optional()])
	summary = TextAreaField('biography', [validators.optional()])

class AuthorForm(Form):
	familyname 	= TextField('familyname', [validators.Required()])
	firstname 	= TextField('firstname', [validators.Required()])
	biography 	= TextAreaField('biography', [validators.optional()])
	dateofbirth 	= DateField('dateofbirth', [validators.optional()])
	placeofbirth 	= TextField('placeofbirth', [validators.optional()])
	nationality 	= TextField('nationality', [validators.optional()])
	website 	= TextField('website', [validators.optional()])
	
	# il faudrait limiter les valeurs à celles qui NE SONT PAS déjà des bouquins de l'auteur X…
	booklist = SelectField('book_list', [validators.optional()])
	portrait = FileField('portrait', [validators.optional(),file_allowed(photos, "Images only!")])

class SearchForm(Form):
	title = TextField('title')
	ean = TextField('ean')
	isbn = TextField('isbn')
	author = TextField('author')