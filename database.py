import py
from flaskext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.Integer)
    name = db.Column(db.Text())
    value = db.Column(db.Text())
