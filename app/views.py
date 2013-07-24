# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, request
from flask.ext.wtf import Form, TextField, BooleanField, DateField, IntegerField, DecimalField, TextAreaField, FileField, file_allowed, validators, Required
from flaskext.uploads import UploadSet, IMAGES, configure_uploads
from app import app, db
from config import AWS_KEY,AMAZON_SECRET_KEY,LANG
from models import Author, Book
from forms import BookForm, AuthorForm, SearchForm, LoginForm
from lxml import objectify
import bottlenose
import os
from werkzeug import secure_filename

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

covers = UploadSet('covers', IMAGES)
configure_uploads(app, covers)

@app.route('/')
@app.route('/index')
def index():
	bk = Book.query.with_entities(Book.id,Book.title).all()
	return render_template("index.html",
	title = 'Index',
	sitename = 'Ma Bibliotheque',books = bk)


@app.route('/book/<number>')
def book(number):
	book = Book.query.filter_by(id = number).first()
	if book.cover != None:
		book.photo_url = covers.url(book.cover)
	return render_template('book.html', sitename = 'Ma Bibliotheque', title = book.title, book = book)

@app.route('/author/<number>')
def author(number):
	author = Author.query.filter_by(id = number).first()
	author.completename = author.firstname + ' ' + author.familyname
	if author.photo != None:
		author.photo_url = photos.url(author.photo)
	return render_template('author.html', sitename = 'Ma Bibliotheque', title = author.completename, author = author)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
		return redirect('/index')
	return render_template('login.html', title = 'Sign In', form = form)

@app.route('/admin')
def admin():
	# compter les auteurs
	aut = Author.query.all()
	authors_number = int()
	for a in aut:
		authors_number += 1
	# compter les livres et volumes/masses
	bk = Book.query.with_entities(Book.length,Book.width,Book.thickness,Book.mass).all()
	#bk = Book.query(width,length,mass).all()
	books_number = int()
	mass_tot = float()
	vol_tot = float()
	len_tot = float()
	for b in bk:
		books_number += 1
		if b[2] != None :
			# rappel : la longueur d'une étagère, c'est en fait tous les bouquins mis cote à cote.
			# soit l'épaisseur accumulée !
			len_tot = len_tot + b[2]
			if b[0] != None :
				vol_tot = vol_tot + (b[0] * b[1] * b[2])
		if b[3] != None :
			mass_tot = mass_tot + b[3]
	dico = dict()
	# le volume vient en cm3. On monte au dm3, soit le litre.
	vol_tot = round(vol_tot / 1000,2)
	dico["aut"] = authors_number
	dico["bk_nb"] = books_number
	# si la masse totale dépasse 700 kg, on passe à la tonne
	if mass_tot > 700:
		dico["bk_mass"] = round(mass_tot / 1000,2)
		dico["bk_mass_unit"] = 'T'
	else:
		dico["bk_mass"] = round(mass_tot,2)
		dico["bk_mass_unit"] = 'kg'
	# si le volume est superieur à 700 litre, on passe au m3
	if vol_tot > 700:
		dico["bk_vol"] = round(vol_tot / 1000,2)
		dico["bk_vol_unit"] = 'm3'
	else:
		dico["bk_vol"] = round(vol_tot,2)
		dico["bk_vol_unit"] = 'litres'
	# longueur
	dico["bk_len"] = len_tot / 100
	return render_template("index_admin.html", sitename = 'Ma Bibliotheque', dico = dico)

@app.route('/edit_author', methods = ['GET', 'POST'])
def edit_author():
	bk = Book.query.with_entities(Book.id,Book.title).all()
	form = AuthorForm()
	if form.validate_on_submit():
		a = Author(firstname= form.firstname.data, familyname= form.familyname.data)
		# on ajoute les élements en dessous, mais s'ils ne sont pas là, c'est pas grave !
		a.nationality= form.nationality.data
		a.dateofbirth= form.dateofbirth.data
		a.placeofbirth = form.placeofbirth.data
		a.website = form.website.data
		a.biography = form.biography.data
		a.books = form.book_list.data
		
		if request.method == 'POST' and 'portrait' in request.files:
			filename = photos.save(request.files['portrait'])
			a.photo = filename
		
		db.session.add(a)
		db.session.commit()
		return redirect('/admin')
	return render_template('edit_author.html', title = 'Ajouter un auteur a la base de donnees', form = form, book_list = bk)

@app.route('/edit_book', methods = ['GET', 'POST'])
def edit_book():
	auts = Author.query.with_entities(Author.id,Author.firstname,Author.familyname).all()
	form = BookForm()
	if form.validate_on_submit():
		b = Book(title = form.title.data)
		# on ajoute les élements en dessous, mais s'ils ne sont pas là, c'est pas grave !
		b.ean = form.ean.data
		b.isbn = form.isbn.data
		b.thickness = form.thickness.data
		b.width = form.width.data
		b.length = form.length.data
		b.summary = form.summary.data
		b.mass = form.mass.data
		b.numberofpages = form.numberofpages.data
		b.publisher = form.publisher.data
		b.authors = form.authors_list.data
		
		if request.method == 'POST' and 'cover' in request.files:
			filename = covers.save(request.files['cover'])
			b.cover = filename
		
		db.session.add(b)
		db.session.commit()
		return redirect('/admin')
	return render_template('edit_book.html', title = 'Ajouter un livre a la base de donnees', form = form, author_list = auts )

@app.route('/search_amazon_book', methods = ['GET', 'POST'])
def search_amazon_book():
	form = SearchForm()
	if form.validate_on_submit():
		amazon = bottlenose.Amazon(AWS_KEY,AMAZON_SECRET_KEY,LANG)
		search = amazon.ItemSearch(EAN=str(form.ean.data), ISBN=str(form.isbn.data), Title=unicode(form.title.data), Author=unicode(form.author.data), SearchIndex='Books', ResponseGroup='Medium')
		#
		# I create a list of each book found with just what I need to identify them. We will be able to modify the book later.
		#
		root = objectify.fromstring(search)
		listing = list()
		for item in root.Items.Item:
			dico = dict()
			dico["title"] = unicode(item.ItemAttributes.Title)
			dico["ASIN"] = unicode(item.ASIN)
			try:
				dico["img"] = 	unicode(item.SmallImage.URL)
			except AttributeError:
				dico["img"] = ''
			try:
				dico["ISBN"] = 	unicode(item.ItemAttributes.ISBN)
			except AttributeError:
				dico["ISBN"] = 0
			try:
				dico["EAN"] = 	int(item.ItemAttributes.EAN)
			except AttributeError:
				dico["EAN"] = 0
			try:
				dico["publisher"] = unicode(item.ItemAttributes.Publisher)
			except AttributeError:
				dico["publisher"] = ''
			auts = list()
			try:
				for author in item.ItemAttributes.Author:
					auts.append(unicode(author))
					dico["authors"] = auts
			except AttributeError:
				dico["authors"] = ''
			listing.append(dico)
		return render_template('list_amazon_results.html',listing = listing)
	return render_template('search_amazon_book.html', title = 'Chercher un livre dans la base de donnees mondiale d\'Amazon', form = form )

@app.route('/add_amazon_book/<asin>', methods = ['GET', 'POST'])
def add_amazon_book(asin):
	amazon = bottlenose.Amazon(AWS_KEY,AMAZON_SECRET_KEY,LANG)
	#
	# we fetch the primary informations from large group amazon search
	#
	fetch = amazon.ItemLookup(IdType='ASIN', ItemId= asin, ResponseGroup='Large')
	xml = objectify.fromstring(fetch)
	dico = dict()
	try:
		dico["title"] = unicode(xml.Items.Item.ItemAttributes.Title)
	except AttributeError:
		dico["title"] = ''
	try:
		dico["img"] = unicode(xml.Items.Item.LargeImage.URL)
	except AttributeError:
		dico["img"] = ''
	try:
		dico["ISBN"] = unicode(xml.Items.Item.ItemAttributes.ISBN)
	except AttributeError:
		dico["ISBN"] = 0
	try:
		dico["EAN"] = int(xml.Items.Item.ItemAttributes.EAN)
	except AttributeError:
		dico["EAN"] = 0
	try:
		dico["publisher"] = unicode(xml.Items.Item.ItemAttributes.Publisher)
	except AttributeError:
		dico["publisher"] = ''
	#
	# amazon works in US units (hundreds-inches and pounds). I want them in kilos and cm, so I import the data in float and translate.
	#
	try:
		thickness = float(xml.Items.Item.ItemAttributes.PackageDimensions.Height)
		dico["thickness"] = round(thickness * 2.54/100, 1)
	except AttributeError:
		dico["thickness"] = ''
	try:
		length = float(xml.Items.Item.ItemAttributes.PackageDimensions.Length)
		dico["length"] = round(length * 2.54/100, 1)
	except AttributeError:
		dico["length"] = ''
	try:
		width = float(xml.Items.Item.ItemAttributes.PackageDimensions.Width)
		dico["width"] = round(width * 2.54/100, 1)
	except AttributeError:
		dico["width"] = ''
	try:
		mass = float(xml.Items.Item.ItemAttributes.PackageDimensions.Weight)
		dico["mass"] = round(mass * 0.45/100,2)
	except AttributeError:
		dico["mass"] = ''
	try:
		dico["pages"] = int(xml.Items.Item.ItemAttributes.NumberOfPages)
	except AttributeError:
		dico["pages"] = ''
	try:
		dico["summary"] = unicode(xml.Items.Item.EditorialReviews.EditorialReview.Content)
	except AttributeError:
		try:
			# sometime amazon doesn't give it the first time !
			fetch2 = amazon.ItemLookup(IdType='ASIN', ItemId= asin, ResponseGroup='EditorialReview')
			xml2 = objectify.fromstring(fetch2)
			dico["summary"] = unicode(xml2.EditorialReview.Content)
		except AttributeError:
			dico["summary"] = ''
	
	#
	# summary comes from the editorial review group search
	#
	#search = amazon.ItemLookup(IdType='ASIN', ItemId= number, ResponseGroup='Large')
	form = BookForm()
	if form.validate_on_submit():
		b = Book(title = form.title.data)	#
		# on ajoute les élements en dessous, mais s'ils ne sont pas là, c'est pas grave !
		b.ean = form.ean.data			#
		b.isbn = form.isbn.data 		#
		b.thickness = form.thickness.data	#
		b.width = form.width.data		#
		b.length = form.length.data		#
		b.summary = form.summary.data
		b.mass = form.mass.data			#
		b.numberofpages = form.numberofpages.data#
		b.publisher = form.publisher.data	#
		db.session.add(b)
		db.session.commit()
		return redirect('/admin')
	return render_template('edit_book.html', form = form, dico = dico)