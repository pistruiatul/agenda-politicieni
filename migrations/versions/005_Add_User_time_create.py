from sqlalchemy import (Table, Column, ForeignKey, MetaData,
                        Integer, Text, String, DateTime)


meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    user = Table(
        'user', meta,
        Column('id', Integer, primary_key=True),
        Column('openid_url', Text),
        Column('name', Text),
        Column('email', Text))

    time_create_c = Column('time_create', DateTime)
    time_create_c.create(user)


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    user = Table(
        'user', meta,
        Column('id', Integer, primary_key=True),
        Column('openid_url', Text),
        Column('name', Text),
        Column('email', Text),
        Column('time_create', DateTime))

    user.c.time_create.drop()
