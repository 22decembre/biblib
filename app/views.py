# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect
from app import app, db
from config import AWS_KEY,AMAZON_SECRET_KEY,LANG
from models import Author, Book
from forms import BookForm, AuthorForm, SearchForm, LoginForm
import bottlenose
import simplexml
import os


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
    title = 'Index',
    sitename = 'Ma Bibliotheque')

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
	form = AuthorForm()
	if form.validate_on_submit():
		a = Author(firstname= form.firstname.data, familyname= form.familyname.data)
		# on ajoute les élements en dessous, mais s'ils ne sont pas là, c'est pas grave !
		a.nationality= form.nationality.data
		a.dateofbirth= form.dateofbirth.data
		a.placeofbirth = form.placeofbirth.data
		a.website = form.website.data
		a.biography = form.biography.data
		db.session.add(a)
		db.session.commit()
		return redirect('/admin')
	return render_template('edit_author.html', title = 'Ajouter un auteur a la base de donnees', form = form)

@app.route('/edit_book', methods = ['GET', 'POST'])
def edit_book():
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
		db.session.add(b)
		db.session.commit()
		return redirect('/admin')
	return render_template('edit_book.html', title = 'Ajouter un livre a la base de donnees', form = form )

@app.route('/search_amazon_book', methods = ['GET', 'POST'])
def search_amazon_book():
	form = SearchForm()
	if form.validate_on_submit():
		amazon = bottlenose.Amazon(AWS_KEY,AMAZON_SECRET_KEY,LANG)
		search = amazon.ItemSearch(EAN=str(form.ean.data), ISBN=str(form.isbn.data), Title=str(form.title.data), Author=str(form.author.data), SearchIndex='Books', ResponseGroup='Medium')
		xml = simplexml.loads(search)
		# I create a list of each book found with just what I need to identify them. We will be able to modify the book later.
		listing = list()
		for item in xml['ItemSearchResponse']['Items']['Item']:
			dico = dict()
			dico["title"] = str(item["ItemAttributes"]["Title"])
			dico["ASIN"] = item["ASIN"]
			if 'SmallImage' in item.keys():
				dico["img"] = item["SmallImage"]["URL"]
			if 'ISBN' in item['ItemAttributes'].keys():
				dico["ISBN"] = 		item["ItemAttributes"]["ISBN"]
			if 'EAN' in item['ItemAttributes'].keys():
				dico["EAN"] = 		item["ItemAttributes"]["EAN"]
			if 'Manufacturer' in item["ItemAttributes"].keys():
				dico["publisher"] = 	item["ItemAttributes"]["Publisher"]
			
			listing.append(dico)
		return render_template('list_amazon_results.html',listing = listing)
	return render_template('search_amazon_book.html', title = 'Chercher un livre dans la base de donnees mondiale d\'Amazon', form = form )

@app.route('/add_amazon_book/<number>', methods = ['GET', 'POST'])
def add_amazon_book(number):
	amazon = bottlenose.Amazon(AWS_KEY,AMAZON_SECRET_KEY,LANG)
	#
	# we fetch the primary informations from large group amazon search
	#
	search = amazon.ItemLookup(IdType='ASIN', ItemId= number, ResponseGroup='Large')
	xml = simplexml.loads(search)
	dico = dict()
	if 'Title' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["title"] = str(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['Title'])
	if 'LargeImage' in xml['ItemLookupResponse']['Items']['Item'].keys():
		dico["img"] = str(xml['ItemLookupResponse']['Items']['Item']['LargeImage']['URL'])
	if 'ISBN' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["ISBN"] = int(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['ISBN'])
	if 'EAN' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["EAN"] = int(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['EAN'])
	if 'Publisher' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["publisher"] = str(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['Publisher'])
	if 'PackageDimensions' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		#
		# amazon works in US units (hundreds-inches and pounds). I want them in kilos and cm, so I import the data in float and translate.
		#
		if 'Height' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions'].keys():
			thickness = float(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions']["Height"])
			dico["thickness"] = round(thickness * 2.54/100, 1)
		if 'Length' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions'].keys():
			length = float(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions']["Length"])
			dico["length"] = round(length * 2.54/100, 1)
		if 'Width' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions'].keys():
			width = float(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions']["Width"])
			dico["width"] = round(width * 2.54/100, 1)
		if 'Weight' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions'].keys():
			mass = float(xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['PackageDimensions']["Weight"])
			dico["mass"] = round(mass * 0.45/100,2)
	if 'NumberOfPages' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["pages"] = xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['NumberOfPages']
	#
	# summary comes from the editorial review group search
	#
	search = amazon.ItemLookup(IdType='ASIN', ItemId= number, ResponseGroup='Large')
	xml = simplexml.loads(search)
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

@app.route('/book/<number>')
def book(number):
	book = Book.query.filter_by(id = number).first()
	return render_template('book.html', title = book.title )

@app.route('/author/<number>')
def author(number):
	author = Author.query.filter_by(id = number).first()
	return render_template('author.html', title = author.firstname )
