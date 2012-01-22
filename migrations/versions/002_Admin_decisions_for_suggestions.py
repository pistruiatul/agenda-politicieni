from sqlalchemy import (Table, Column, ForeignKey, MetaData,
                        Integer, Text, String, DateTime)


meta = MetaData()


user = Table(
    'user', meta,
    Column('id', Integer, primary_key=True),
    Column('openid_url', Text),
    Column('name', Text),
    Column('email', Text))


person = Table(
    'person', meta,
    Column('id', Integer, primary_key=True),
    Column('name', Text))


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    suggestion = Table(
        'suggestion', meta,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('user.id')),
        Column('person_id', Integer, ForeignKey('person.id')),
        Column('name', String(30)),
        Column('value', Text()),
        Column('date', DateTime(timezone=True)))

    admin_id_c = Column('admin_id', Integer,
                        ForeignKey('user.id'))
    admin_id_c.create(suggestion)

    admin_decision_c = Column('decision', String(10))
    admin_decision_c.create(suggestion)


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    suggestion = Table(
        'suggestion', meta,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('user.id')),
        Column('person_id', Integer, ForeignKey('person.id')),
        Column('name', String(30)),
        Column('value', Text()),
        Column('date', DateTime(timezone=True)),
        Column('admin_id', Integer, ForeignKey('user.id')),
        Column('decision', String(10)))

    suggestion.c.admin_id.drop()
    suggestion.c.decision.drop()
