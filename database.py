import os.path
from flask import json
from flaskext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.Integer)
    name = db.Column(db.Text())
    value = db.Column(db.Text())


def import_fixture(flush=True):
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    fixture_path = os.path.join(data_path, 'fixture.json')

    if flush:
        db.drop_all()
        db.create_all()

    with open(fixture_path, 'rb') as f:
        fixture = json.load(f)

    for person in fixture:
        person_id = person.pop('id')
        for key in person:
            record = Contact(person=person_id, name=key)
            record.value = person[key]
            db.session.add(record)

    db.session.commit()
