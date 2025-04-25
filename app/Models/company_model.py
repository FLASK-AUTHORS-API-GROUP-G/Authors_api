from app.extensions import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = "companys"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('company', uselist=False))  # one-to-one relationship
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, name, origin, description, location, company_id):
        self.name = name
        self.origin = origin
        self.description = description
        self.location = location
        self.author_id = company_id
