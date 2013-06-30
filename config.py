# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# DB TYPE
SQL = 'sqlite'

# FOR SERVER DATABASES : ORACLE, MYSQL, POSTGRESQL
SQL_HOST = ''
SQL_DB = ''
SQL_USER = ''
SQL_PASS = ''
SQL_PORT = ''

#SQLALCHEMY_DATABASE_URI = SQL + ', username=' + SQL_USER + ', password=' + SQL_PASS + ', host=' + SQL_HOST + ', port= ' + SQL_PORT + ', database=' + SQL_DB

if SQL == 'sqlite' :
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
	
else :
	if SQL_HOST == '' :
		SQL_HOST = 'localhost'

	if SQL_USER == '' :
		SQL_USER = 'biblib'

	if SQL_PORT != '' :
		SQLALCHEMY_DATABASE_URI = SQL + '://' + SQL_USER + ':' + SQL_PASS + '@' + SQL_HOST + ':' + SQL_PORT + '/' + SQL_DB

	else :
		SQLALCHEMY_DATABASE_URI = SQL + '://' + SQL_USER + ':' + SQL_PASS + '@' + SQL_HOST + '/' + SQL_DB

#mysql://scott:tiger@localhost/foo

#SQLALCHEMY_DATABASE_URI = SQL + '://' +
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')