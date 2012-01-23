from sqlalchemy import (Table, Column, ForeignKey, MetaData,
                        Integer, Text, String, DateTime, LargeBinary)


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


content_version = Table(
    'content_version', meta,
    Column('id', Integer, primary_key=True),
    Column('person_id', Integer, ForeignKey('person.id')),
    Column('content', LargeBinary),
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('time', DateTime))


property = Table(
    'property', meta,
    Column('id', Integer, primary_key=True),
    Column('person_id', Integer, ForeignKey('person.id')),
    Column('name', String(30)),
    Column('value', Text()))


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    content_version.create()

    import agenda, database
    with agenda.create_app().test_request_context():
        database.migrate_properties_to_content()

    property.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    property.create()
    content_version.drop()
