# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.ldap import LDAP, login_required

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, models
