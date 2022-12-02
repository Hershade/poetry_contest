import datetime

from database import db


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    contestants = db.relationship('Contestant', backref='type')


class Gender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    contestants = db.relationship('Contestant', backref='genders')


class University_Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    contestants = db.relationship('Contestant', backref='university_career')


class Contestant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_card = db.Column(db.String(6), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(250), nullable=False)
    birthdate = db.Column(db.types.DateTime, nullable=False)
    types_id = db.Column(db.Integer(), db.ForeignKey(Type.id))
    genders_id = db.Column(db.Integer(), db.ForeignKey(Gender.id))
    university_careers_id = db.Column(db.Integer(), db.ForeignKey(University_Career.id))
    inscription_date = db.Column(db.types.DateTime(timezone=True), default=datetime.datetime.utcnow)
    participation_date = db.Column(db.types.DateTime(timezone=True))


