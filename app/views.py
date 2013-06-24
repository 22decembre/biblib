# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = { 'nickname': 'Miguel' } # fake user
    return render_template("index.html",
    title = 'Index',
    sitename = 'Ma Bibliotheque')
    
    
@app.route('/add_author', methods = ['GET', 'POST'])
def add_author():
    form = LoginForm()
    return render_template('add_author.html', 
        title = 'Add an author to the database',
        form = form)
        
@app.route('/add_book', methods = ['GET', 'POST'])
def add_book():
    form = LoginForm()
    return render_template('add_book.html', 
        title = 'Add a book to the database',
        form = form_book)