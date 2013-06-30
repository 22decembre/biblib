# -*- coding: utf-8 -*-

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# DB TYPE
SQL = 'mysql'

# FOR SERVER DATABASES : ORACLE, MYSQL, POSTGRESQL
SQL_HOST = 'blackblock.22decembre.eu'
SQL_DB = 'biblib'
SQL_USER = 'biblib'
SQL_PASS = ''
SQL_PORT = ''

# SQLITE ONLY
SQLITE = ''


#mysql://scott:tiger@localhost/foo

SQLALCHEMY_DATABASE_URI = SQL + '://' +
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')