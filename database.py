import os.path
from datetime import datetime
from collections import defaultdict
from flask import json
from flaskext.sqlalchemy import SQLAlchemy
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


_data_dir = os.path.join(os.path.dirname(__file__), 'data')
with open(os.path.join(_data_dir, 'prop_defs.json'), 'rb') as f:
    prop_defs = json.load(f)
with open(os.path.join(_data_dir, 'hartapoliticii.json'), 'rb') as f:
    hartapoliticii_data = dict((int(k), v) for k, v in
                               json.load(f).iteritems())
meta_defs = ['office', 'college']


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openid_url = db.Column(db.Text())
    name = db.Column(db.Text())
    email = db.Column(db.Text())
    time_create = db.Column(db.DateTime)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())

    def get_content(self):
        version = self.versions.order_by(ContentVersion.time.desc()).first()
        return {} if version is None else version.get_content()

    def save_content_version(self, new_content, user):
        utcnow = datetime.utcnow()
        version = ContentVersion(person=self, user=user, time=utcnow)
        version.content = json.dumps(new_content)
        db.session.add(version)
        db.session.commit()
        log.info("Content update for person id=%d version_id=%d",
                 self.id, version.id)

    def get_meta(self, key):
        meta = self.meta.filter_by(key=key).first()
        return None if meta is None else meta.value


class ContentVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person',
        backref=db.backref('versions', lazy='dynamic'))
    content = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    time = db.Column(db.DateTime)

    def get_content(self):
        return json.loads(self.content)


class PersonMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person',
        backref=db.backref('meta', lazy='dynamic'))
    key = db.Column(db.Text)
    value = db.Column(db.Text)


def import_json(json_path):
    utcnow = datetime.utcnow()
    count = defaultdict(int)

    with open(json_path, 'rb') as f:
        people_data = json.load(f)

    for person_data in people_data['persons']:
        found_persons = Person.query.filter_by(name=person_data['name']).all()
        if found_persons:
            assert len(found_persons) == 1
            person = found_persons[0]

        else:
            person = Person(name=person_data['name'])
            db.session.add(person)
            log.info('New person %r', person_data['name'])
            count['new-person'] += 1

        content = {}
        for key in prop_defs:
            values = person_data.get(key, [])
            if values:
                content['key'] = values

        if content != person.get_content():
            version = ContentVersion(person=person, time=utcnow)
            version.content = json.dumps(content)
            db.session.add(version)
            log.info('Content update for person id=%d', person.id)
            count['new-version'] += 1

        for key in meta_defs:
            value = person_data.get('_meta', {}).get(key, None)
            if value is None:
                continue
            meta = person.meta.filter_by(key=key).first()
            if meta is None:
                meta = PersonMeta(person=person, key=key, value=value)
            else:
                meta.value = value
            db.session.add(meta)

    db.session.commit()
    if count:
        log.info("JSON import from %r completed; %r", json_path, dict(count))


def fix_senator_names(json_path):
    with open(json_path, 'rb') as f:
        for s in json.load(f):
            persons = Person.query.filter_by(name=s['inverse_name']).all()
            assert len(persons) == 1
            [person] = persons
            person.name = s['name']
            db.session.add(person)
    db.session.commit()


def get_user(openid_url):
    return User.query.filter_by(openid_url=openid_url).first()


def get_update_user(openid_url, name, email):
    user = get_user(openid_url)
    if user is None:
        utcnow = datetime.utcnow()
        user = User(openid_url=openid_url, time_create=utcnow)
        log.info("New user, openid_url=%r", openid_url)

    if (name, email) != (user.name, user.email):
        user.name = name
        user.email = email
        db.session.add(user)
        db.session.commit()
        log.info("User data modified for openid_url=%r: name=%r, email=%r",
                 openid_url, name, email)

    return user
