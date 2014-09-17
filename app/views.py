# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, request
#from flask.ext.login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from wtforms import Form, TextField, BooleanField, DateField, IntegerField, DecimalField, TextAreaField, FileField, validators
from app import app, db
#from config import AWS_KEY,AMAZON_SECRET_KEY,LANG, 
#from config import AUTH_SYSTEM
from models import Author, Book, author_book
from forms import BookForm, AuthorForm, SearchForm, LoginForm, DeleteForm
from lxml import objectify
import bottlenose
#import simpleldap
import os
from werkzeug.datastructures import FileStorage

#if AUTH_SYSTEM == 'basic':
from flask.ext.basicauth import BasicAuth
auth = BasicAuth(app)

### présentation

@app.route('/')
@app.route('/index')
def index():
	bk = Book.query.all()
	auts = Author.query.with_entities(Author.id,Author.firstname,Author.familyname,Author.books).all() 
	return render_template("index.html",
	title = 'Index',
	sitename = 'Ma Bibliotheque',books = bk)


@app.route('/book/<number>')
def book(number):
	book = Book.query.get(number)
	if os.path.exists('app/static/covers/' + str(book.id)):
		book.img = True
	return render_template('book.html', sitename = 'Ma Bibliotheque', title = book.title, book = book)

@app.route('/author/<number>')
def author(number):
	author = Author.query.get(number)
	if os.path.exists('app/static/photos/' + str(author.id)):
		author.img = True
	return render_template('author.html', sitename = 'Ma Bibliotheque', title = author, author = author)

### login / ldap

#login_manager = LoginManager()
#login_manager.init_app(app)
#login_manager.login_view = 'login'

#@app.before_request
#def before_request():
    #g.user = current_user

#class User(UserMixin):
	#def __init__(self, uid=None, name=None, passwd=None):

		#self.active = False
		
		#ldapres = ldap_fetch(uid=uid, name=name, passwd=passwd)

		#if ldapres is not None:
			#self.name = ldapres['name']
			#self.id = ldapres['id']
			## assume that a disabled user belongs to group 404
			#if ldapres['gid'] != 404:
				#self.active = True
			#self.gid = ldapres['gid']

	#def is_active(self):
		#return self.active

	#def is_authenticated(self):
		#return True
	
	#def get_id(self):
		#return self.id   

#def ldap_name(name):
	#return '{0}={1},{2}'.format(LDAP_ID, name, LDAP_BASE_DN)
		
#def ldap_fetch(uid=None, name=None, passwd=None):
	#try:
		#if name is not None and passwd is not None:
			#l = simpleldap.Connection(LDAP_HOST,dn=ldap_name(name),password=passwd)
			#r = l.search('uid={0}'.format(name), base_dn=LDAP_BASE_DN)
		#else:
			#l = simpleldap.Connection(LDAP_HOST)
			#r = l.search('uidNumber={0}'.format(uid), base_dn=LDAP_BASE_DN)
		#return {
			#'name': r[0]['uid'][0],
			#'id': unicode(r[0]['uidNumber'][0]),
			#'gid': int(r[0]['gidNumber'][0])
			#}
	#except:
		#return None

#@login_manager.user_loader
#def load_user(userid):
	#return User(uid=userid)

#@app.route("/login", methods=["GET", "POST"])
#def login():
	#if g.user is not None and g.user.is_authenticated():
		#return redirect('admin')
	#form = LoginForm()
	#if request.method == 'POST' and form.validate():
		#user = User(name=form.username.data, passwd=form.password.data)
		
		#if user.active:
			#login_user(user)
			#flash("Logged in successfully.")
			#return redirect("/admin")
	#return render_template("login.html", form=form)


#@app.route("/logout", methods=["GET", "POST"])
#@login_required
#def logout():
	#logout_user()
	#return redirect("/")

### admin / backend

@app.route('/admin')
@auth.required
def admin():
	# compter les auteurs
	bk = Book.query.with_entities(Book.id,Book.title).all()
	aut = Author.query.all()
	authors_number = int()
	for a in aut:
		authors_number += 1
	# compter les livres et volumes/masses
	bk = Book.query.with_entities(Book.length,Book.width,Book.thickness,Book.mass,Book.id,Book.title).all()
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
	return render_template("index_admin.html", sitename = 'Ma Bibliotheque', dico = dico, books_list = bk, authors_list = aut)

@app.route('/delete_authors', methods = ['GET', 'POST'])
@auth.required
def delete_authors():
	form = DeleteForm()
	auts = Author.query.all()
	if form.request=='POST' and form.validate():
		for item in request.form.getlist('delete'):
			a = Author.query.get(item)
			if a.books:
				for book in a.books:
					a.remove_book(book)
				db.session.commit()
			if os.path.exists('app/static/photos/' + str(a.id)):
				os.remove('app/static/photos/' + str(a.id))
			db.session.delete(a)
		db.session.commit()
		return redirect('/admin')
	return render_template("delete_authors.html",
	title = 'Eliminer un ou des auteurs de la bibliotheque',
	sitename = 'Ma Bibliotheque',listing = auts, form = form)

@app.route('/delete_books', methods = ['GET', 'POST'])
#@auth.required
def delete_books():
	form = DeleteForm()
	bk = Book.query.with_entities(Book.id,Book.title).all()
	#if form.validate_on_submit():
	if form.request=='POST' and form.validate():
		for item in request.form.getlist('delete'):
			a = Book.query.get(item)
			if a.authors:
				for author in a.authors:
					a.remove_author(author)
				db.session.commit()
			if os.path.exists('app/static/covers/' + str(a.id)):
				os.remove('app/static/covers/' + str(a.id))
			db.session.delete(a)
		db.session.commit()
		return redirect('/admin')
	return render_template("delete_books.html", title = 'Eliminer un ou des livres de la bibliotheque', sitename = 'Ma Bibliotheque',listing = bk, form = form)

@app.route('/edit_author/<number>', methods = ['GET', 'POST'])
@auth.required
def edit_author(number):
	if number == 'new':
		author = Author()
		title = 'Ajouter un auteur dans la bibliotheque'
	else:
		author = Author.query.get(number)
		title = author
		if os.path.exists('app/static/photos/' + str(author.id)):
			author.img = True
	#global author
	#a = author
	form = AuthorForm()
	form.booktoadd.choices = Book.query.filter(Book!=author.books)
	update = False
	#if form.validate_on_submit():
	if request.form=='POST' and form.validate():
		#print form.errors
		author.firstname = unicode(form.firstname.data)
		author.familyname = unicode(form.familyname.data)
		if form.nationality.data != author.nationality:
			author.nationality= unicode(form.nationality.data)
			update = True
		#a.dateofbirth= form.dateofbirth.data
		if form.placeofbirth.data != author.placeofbirth:
			author.placeofbirth = unicode(form.placeofbirth.data)
			update = True
		if form.website.data != author.website:
			author.website = unicode(form.website.data)
			update = True
		if form.biography.data != author.biography:
			author.biography = unicode(form.biography.data)
			update = True

		# gestion des livres
		if request.form.getlist('booktodelete'):
			for item in request.form.getlist('booktodelete'):
				a = Book.query.get(item)
				author.remove_book(a)
				update = True
		
		if request.form.getlist('booktoadd'):
			for item in request.form.getlist('booktoadd'):
				# even if noting is select, the field return something, a unicode string '__None'
				# this "if" not to block the whole thing. Same on books !
				if item != '__None':
					a = Book.query.get(item)
					author.add_book(a)
					update = True
		
		if update:
			db.session.add(author)
			db.session.commit()
			db.session.refresh(author)
		
		# the photo will overwrite the previous if existing.
		# thus, only one per author and nothing else to check
		if request.method == 'POST' and request.files['portrait']:
			fileurl = 'app/static/photos/' + str(author.id)
			image = request.files['portrait'].save(fileurl)
		
		return redirect('/admin')
	return render_template('edit_author.html', form = form, author = author, title = title)

@app.route('/edit_book/<number>', methods = ['GET', 'POST'])
@auth.required
def edit_book(number):
	amazon_img = False
	if number == 'new':
		book = Book()
		book.mass = 0
		book.width = 0
		book.length = 0
		book.thickness = 0
		title = 'Ajouter un livre dans la bibliotheque'
	elif number[0:7] == 'amazon:':
		import urllib
		asin=unicode(number[7:])
		amazon = bottlenose.Amazon(AWS_KEY,AMAZON_SECRET_KEY,LANG)
		#
		# we fetch the primary informations from large group amazon search
		#
		fetch = amazon.ItemLookup(IdType='ASIN', ItemId= asin, ResponseGroup='Large')
		xml = objectify.fromstring(fetch)
		book = Book()
		try:
			book.title = unicode(xml.Items.Item.ItemAttributes.Title)
		except AttributeError:
			book.title = ''
		try:
			amazon_img = unicode(xml.Items.Item.LargeImage.URL)
		except AttributeError:
			amazon_img = ''
		try:
			book.isbn = unicode(xml.Items.Item.ItemAttributes.ISBN)
		except AttributeError:
			book.isbn = ''
		try:
			book.ean = unicode(xml.Items.Item.ItemAttributes.EAN)
		except AttributeError:
			book.ean = ''
		try:
			book.publisher = unicode(xml.Items.Item.ItemAttributes.Publisher)
		except AttributeError:
			book.publisher = ''
		
		#
		# amazon works in US units (hundreds-inches and pounds). I want them in kilos and cm, so I import the data in float and translate.
		#
		try:
			thickness = float(xml.Items.Item.ItemAttributes.PackageDimensions.Height)
			book.thickness = round(thickness * 2.54/100, 1)
		except AttributeError:
			book.thickness = ''
		try:
			length = float(xml.Items.Item.ItemAttributes.PackageDimensions.Length)
			book.length = round(length * 2.54/100, 1)
		except AttributeError:
			book.length = ''
		try:
			width = float(xml.Items.Item.ItemAttributes.PackageDimensions.Width)
			book.width = round(width * 2.54/100, 1)
		except AttributeError:
			book.width = ''
		try:
			mass = float(xml.Items.Item.ItemAttributes.PackageDimensions.Weight)
			book.mass = round(mass * 0.45/100,2)
		except AttributeError:
			book.mass = ''
		try:
			book.numberofpages = int(xml.Items.Item.ItemAttributes.NumberOfPages)
		except AttributeError:
			book.numberofpages = ''
		try:
			book.summary = unicode(xml.Items.Item.EditorialReviews.EditorialReview.Content)
		except AttributeError:
			book.summary = ''
		title = 'Ajouter un livre d\'Amazon dans la bibliotheque'

	else:
		book = Book.query.get(number)
		title = book.title
		if os.path.exists('app/static/covers/' + str(book.id)):
			book.img = True
	form = BookForm()
	form.authortoadd.choices = Author.query.filter(Author!=book.authors)
	update = False
	#if form.validate_on_submit():
	if request.form=='POST' and form.validate():
		#print form.errors
		book.title = unicode(form.title.data)
		# on ajoute les élements en dessous, mais s'ils ne sont pas là, c'est pas grave !
		if form.ean.data != book.ean:
			book.ean = unicode(form.ean.data)
			update = True
		if form.isbn.data != book.isbn:
			book.isbn = unicode(form.isbn.data)
			update = True
		if form.thickness.data != book.thickness:
			book.thickness = unicode(form.thickness.data)
			update = True
		if form.width.data != book.width:
			book.width = unicode(form.width.data)
			update = True
		if form.length.data != book.length:
			book.length = form.length.data
			update = True
		if form.summary.data != book.summary and form.summary.data != None:
			book.summary = unicode(form.summary.data)
			update = True
		if form.mass.data != book.mass:
			book.mass = form.mass.data
			update = True
		#if form.numberofpages.data != book.numberofpages:
		#	book.numberofpages = int(form.numberofpages.data)
		#	if type(book.numberofpages) == 'int'
		#		update = True
		if form.publisher.data != book.publisher and form.publisher.data != None:
			book.publisher = unicode(form.publisher.data)
			update = True
		#
		# gestion des auteurs
		if request.form.getlist('authortodelete'):
			for item in request.form.getlist('authortodelete'):
				a = Author.query.get(item)
				book.remove_author(a)
				update = True
		#
		if request.form.getlist('authortoadd'):
			for item in request.form.getlist('authortoadd'):
				# Same as authors, see upside.
				if item != '__None':
					a = Author.query.get(item)
					book.add_author(a)
					update = True
		# adding the book to the db
		if update:
			db.session.add(book)
			db.session.commit()
			db.session.refresh(book)
		
		image_finale = False
		
		if amazon_img:
			image_finale = urllib.urlopen(amazon_img)
			
		if request.method == 'POST' and request.files['cover']:
			image_finale = request.files['cover']
			
		if image_finale:
			fileurl = 'app/static/covers/' + str(book.id)
			image = FileStorage(image_finale).save(fileurl)
				
		return redirect('/admin')
	return render_template('edit_book.html', form = form, book = book, title = title, amazon_img = amazon_img)

@app.route('/search_amazon_book', methods = ['GET', 'POST'])
@auth.required
def search_amazon_book():
	form = SearchForm()
	if request.form=='POST' and form.validate():
	#if form.validate_on_submit():
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
