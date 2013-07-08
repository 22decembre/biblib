# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect
from app import app, db
from models import Author, Book
from forms import BookForm, AuthorForm, SearchForm, LoginForm
import amazonproduct
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
		amazon_api = ProductAdvertisingAPI(AWS_KEY,AMAZON_SECRET_KEY,LANG)
		search = amazon_api.item_lookup(form.ean.data, IdType='EAN', SearchIndex='Books', ResponseGroup='Reviews')
		return redirect('/list_amazon_results',)
	return render_template('search_amazon_book.html', title = 'Chercher un livre dans la base de donnees mondiale d\'Amazon', form = form )
	
@app.route('/list_amazon_results', methods = ['GET', 'POST'])
def search_amazon_book():
	return render_template('list_amazon_results.html', title = 'Chercher un livre dans la base de donnees mondiale d\'Amazon', form = form )

@app.route('/book/<number>')
def book(number):
	book = Book.query.filter_by(id = number).first()
	return render_template('book.html', title = book.title )

@app.route('/author/<number>')
def author(number):
	author = Author.query.filter_by(id = number).first()
	return render_template('author.html', title = author.firstname )
