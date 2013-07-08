# -*- coding: utf-8 -*-

from flask.ext.wtf import Form, TextField, BooleanField, DateField, IntegerField, DecimalField, TextAreaField, validators
from flask.ext.wtf import Required

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
	summary = TextAreaField('summary', [validators.optional()])

class AuthorForm(Form):
	familyname = TextField('familyname', [validators.Required()])
	firstname = TextField('firstname', [validators.Required()])
	biography = TextAreaField('biography', [validators.optional()])
	dateofbirth = DateField('dateofbirth', [validators.optional()])
	placeofbirth = TextField('placeofbirth', [validators.optional()])
	nationality = TextField('nationality', [validators.optional()])
	website = TextField('website', [validators.optional()])

class SearchForm(Form):
	title = TextField('title')
	ean = TextField('ean')
	isbn = TextField('isbn')
	author = TextField('author')