# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect
from app import app
from forms import BookForm, AuthorForm

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
    title = 'Index',
    sitename = 'Ma Bibliotheque')
    
    
@app.route('/add_author', methods = ['GET', 'POST'])
def add_author():
    form = AuthorForm()
    return render_template('add_author.html', 
        title = 'Ajouter un auteur a la base de donnees',
        form = form)
        
@app.route('/add_book', methods = ['GET', 'POST'])
def add_book():
    form = BookForm()
    return render_template('add_book.html', 
        title = 'Ajouter un livre a la base de donnees',
        form = form )