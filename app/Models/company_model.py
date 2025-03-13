from app.extensions import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = "companys"  # Keeping "companys" as the table name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    origin = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))  # Foreign key for Author
    description = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Changed to DateTime

    author = db.relationship('Author', backref='companys')  # Keeping "companys" in backref

    def __init__(self, name, origin, author_id, description, location, created_at=None):
        self.name = name
        self.origin = origin
        self.author_id = author_id
        self.description = description
        self.location = location
        self.created_at = created_at or datetime.utcnow()

    def company_details(self):
        return f"Company '{self.name}' is based in {self.origin}, located at {self.location}. Description: {self.description}. Created on {self.created_at}."
