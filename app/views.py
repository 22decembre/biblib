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

@app.route('/add_author', methods = ['GET', 'POST'])
def add_author():
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
		return redirect('/index')
	return render_template('add_author.html', title = 'Ajouter un auteur a la base de donnees', form = form)

@app.route('/add_book', methods = ['GET', 'POST'])
def add_book():
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
		return redirect('/index')
	return render_template('add_book.html', title = 'Ajouter un livre a la base de donnees', form = form )

@app.route('/search_amazon_book', methods = ['GET', 'POST'])
def search_amazon_book():
	form = SearchForm()
	if form.validate_on_submit():
		amazon = bottlenose.Amazon(AWS_KEY,AMAZON_SECRET_KEY,LANG)
		search = amazon.ItemSearch(EAN=form.ean.data, ISBN=form.isbn.data, Title=form.title.data, Author=form.author.data, SearchIndex='Books', ResponseGroup='Medium')
		xml = simplexml.loads(search)
		# I create a list of each book found with just what I need to identify them. We will be able to modify the book later.
		listing = list()
		for item in xml['ItemSearchResponse']['Items']['Item']:
			dico = dict()
			dico["title"] = item['ItemAttributes']['Title']
			dico["ASIN"] = item['ASIN']
			if 'SmallImage' in item.keys():
				dico["img"] = item['SmallImage']['URL']
			if 'ISBN' in item['ItemAttributes'].keys():
				dico["ISBN"] = 		item['ItemAttributes']['ISBN']
			if 'EAN' in item['ItemAttributes'].keys():
				dico["EAN"] = 		item['ItemAttributes']['EAN']
			if 'Manufacturer' in item['ItemAttributes'].keys():
				dico["publisher"] = 	item['ItemAttributes']['Publisher']
			
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
		dico["title"] = xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['Title']
	if 'LargeImage' in xml['ItemLookupResponse']['Items']['Item'].keys():
		dico["img"] = xml['ItemLookupResponse']['Items']['Item']['LargeImage']['URL']
	if 'ISBN' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["ISBN"] = xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['ISBN']
	if 'EAN' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["EAN"] = xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['EAN']
	if 'Publisher' in xml['ItemLookupResponse']['Items']['Item']['ItemAttributes'].keys():
		dico["publisher"] = xml['ItemLookupResponse']['Items']['Item']['ItemAttributes']['Publisher']
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
		return redirect('/index')
	return render_template('add_book.html', form = form, dico = dico)

@app.route('/book/<number>')
def book(number):
	book = Book.query.filter_by(id = number).first()
	return render_template('book.html', title = book.title )

@app.route('/author/<number>')
def author(number):
	author = Author.query.filter_by(id = number).first()
	return render_template('author.html', title = author.firstname )
