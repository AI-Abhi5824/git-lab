from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Guard(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


class Student(db.Model):
    prn = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    branch = db.Column(db.String(80), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    photo_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active")


class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prn = db.Column(db.String(12), nullable=False)
    guard = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    result = db.Column(db.String(120), nullable=False)
