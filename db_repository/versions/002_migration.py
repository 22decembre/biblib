from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
author_book = Table('author_book', post_meta,
    Column('author', Integer),
    Column('book', Integer),
)

book__author = Table('book__author', post_meta,
    Column('book', Integer, primary_key=True, nullable=False),
    Column('author', Integer, primary_key=True, nullable=False),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['author_book'].create()
    post_meta.tables['book__author'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['author_book'].drop()
    post_meta.tables['book__author'].drop()
