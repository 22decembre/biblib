from app import db

class Author(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(64), index = True)
    familyname = db.Column(db.String(120), index = True)
    website = db.Column(db.String(120))
    dateofbirth = db.Column(db.DateTime)
    placeeofbirth = db.Column(db.String(120))
    nationality = db.Column(db.String(120))
    biography = db.Column(db.Text)

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