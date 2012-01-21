import os.path
from datetime import datetime
from flask import json
from flaskext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person',
        backref=db.backref('properties', lazy='dynamic'))
    name = db.Column(db.String(30))
    value = db.Column(db.Text())


class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    name = db.Column(db.String(30))
    value = db.Column(db.Text())
    date = db.Column(db.DateTime(timezone=True))


def get_persons():
    results = {}

    for person in Person.query.all():
        results[person.id] = person_data = {'name': person.name}

        for prop in person.properties.all():
            person_data[prop.name] = prop.value

    return results


def save_suggestion(person_id, name, value):
    suggestion = Suggestion(person_id=person_id,
                            name=name,
                            value=value,
                            date=datetime.utcnow())
    db.session.add(suggestion)
    db.session.commit()


def import_fixture(flush=True):
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    fixture_path = os.path.join(data_path, 'fixture.json')

    if flush:
        db.drop_all()
        db.create_all()

    with open(fixture_path, 'rb') as f:
        fixture = json.load(f)

    for person_data in fixture:

        person = Person(id=person_data.pop('id'), name=person_data.pop('name'))
        db.session.add(person)

        for key in person_data:
            prop = Property(person=person, name=key, value=person_data[key])
            db.session.add(prop)

    db.session.commit()
