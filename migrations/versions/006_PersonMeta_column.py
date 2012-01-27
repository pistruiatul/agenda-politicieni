from sqlalchemy import (Table, Column, ForeignKey, MetaData,
                        Integer, Text)


meta = MetaData()


person = Table(
    'person', meta,
    Column('id', Integer, primary_key=True),
    Column('name', Text))


person_meta = Table(
    'person_meta', meta,
    Column('id', Integer, primary_key=True),
    Column('person_id', Integer, ForeignKey('person.id')),
    Column('key', Text),
    Column('value', Text))


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    person_meta.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    person_meta.drop()
