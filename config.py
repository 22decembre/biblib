# -*- coding: utf-8 -*-

import os
from app import app

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
LANG = 'fr'

AWS_KEY = 'AKIAJFESEM3FR6WMMKLA'
AMAZON_SECRET_KEY = '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'


### authentication

AUTH_SYSTEM = 'basic'

# use of flask-basicauth : AUTH='basic'
BASIC_AUTH_USERNAME = 'john'
BASIC_AUTH_PASSWORD = 'matrix'

# or ldap with flask-simpleldap : AUTH='ldap'
LDAP_HOST = 'blackblock.22decembre.eu'
LDAP_DOMAIN = '22decembre.eu'
LDAP_BASE_DN = 'ou=users,dc=22decembre,dc=eu'
LDAP_ID = 'uid'

# DB TYPE
SQL = 'sqlite'

# FOR SERVER DATABASES : ORACLE, MYSQL, POSTGRESQL
SQL_HOST = 'blackblock.22decembre.eu'	# defaut : localhost in case of empty
SQL_DB = ''				# defaut : biblib in cas of empty
SQL_USER = ''				# defaut : biblib in cas of empty
SQL_PASS = 'G3bmuqe5QKFZ5G3y'
SQL_PORT = ''				# defaut engine port in case of empty

if SQL == 'sqlite' :
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	
else :
	if SQL_HOST == '' :
		SQL_HOST = 'localhost'

	if SQL_USER == '' :
		SQL_USER = 'biblib'
		
	if SQL_DB == '' :
		SQL_DB = 'biblib'

	if SQL_PORT != '' :
		SQLALCHEMY_DATABASE_URI = SQL + '://' + SQL_USER + ':' + SQL_PASS + '@' + SQL_HOST + ':' + SQL_PORT + '/' + SQL_DB

	else :
		SQLALCHEMY_DATABASE_URI = SQL + '://' + SQL_USER + ':' + SQL_PASS + '@' + SQL_HOST + '/' + SQL_DB

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')