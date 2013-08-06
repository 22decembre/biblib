from app import db

author_book = db.Table('author_book',
    db.Column('author', db.Integer, db.ForeignKey('author.id')),
    db.Column('book', db.Integer, db.ForeignKey('book.id'))
)

class Author(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	firstname = db.Column(db.String(64), index = True)
	familyname = db.Column(db.String(120), index = True)
	website = db.Column(db.String(120))
	dateofbirth = db.Column(db.DateTime)
	placeofbirth = db.Column(db.String(120))
	nationality = db.Column(db.String(120))
	biography = db.Column(db.Text)
	books = db.relationship('Book', secondary=author_book,backref=db.backref('author', lazy='dynamic'))
	
	def __repr__(self):
		rep = self.firstname + ' ' + self.familyname
		return rep.title()
	
	def add_book(self, book):
		self.books.append(book)
		return self
	
	def remove_book(self, book):
		self.books.remove(book)
		return self

class Book(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	ean = db.Column(db.Integer)
	isbn = db.Column(db.Integer)
	title = db.Column(db.String(120), index = True)
	publisher = db.Column(db.String(120), index = True)
	mass = db.Column(db.Float)
	width = db.Column(db.Float)
	thickness = db.Column(db.Float)
	length = db.Column(db.Float)
	numberofpages = db.Column(db.Integer)
	summary = db.Column(db.Text)
	authors = db.relationship('Author', secondary=author_book,backref=db.backref('book', lazy='dynamic'))

	def __repr__(self):
		return '<%r>' % (self.title)

	def remove_author(self, author):
		self.authors.remove(author)
		return self
	
	def add_author(self, author):
		self.authors.append(author)
		return self