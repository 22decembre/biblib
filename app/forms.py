# -*- coding: utf-8 -*-

from flask.ext.wtf import Form, TextField, BooleanField, DateField, IntegerField, DecimalField, TextAreaField
from flask.ext.wtf import Required

class BookForm(Form):
	title = TextField('title', validators = [Required()])
	ean = TextField('ean')
	isbn = TextField('isbn')
	publisher = TextField('publisher')
	thickness = DecimalField('thickness')
	width = DecimalField('width')
	length = DecimalField('length')
	mass = DecimalField('mass')
	numberofpages = IntegerField('numberofpages')
	summary = TextAreaField('summary')
	
class AuthorForm(Form):
	familyname = TextField('familyname', validators = [Required()])
	firstname = TextField('firstname', validators = [Required()])
	biography = TextAreaField('biography')
	dateofbirth = DateField('dateofbirth')
	placeofbirth = TextField('placeofbirth')
	nationality = TextField('nationality')
	website = TextField('website')