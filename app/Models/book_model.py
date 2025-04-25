from app.extensions import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    price = db.Column(db.String(50), nullable=False)  # Added missing price field
    description = db.Column(db.String(50), nullable=False)
    number_of_pages = db.Column(db.String(50), nullable=False)  # Removed unique=True
    price_unit = db.Column(db.String(50), nullable=False)  # Removed unique=True
    publication_date = db.Column(db.DateTime, nullable=False, default=datetime.now)  # Changed to DateTime
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companys.id'))
    author = db.relationship('Author', backref='books')
    company = db.relationship('Company', backref='books')
    other_books = db.Column(db.String(30), default='author')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, title, price, description, number_of_pages, price_unit, author_id, company_id, other_books="author", created_at=None, publication_date=None):
        self.title = title
        self.price = price
        self.description = description
        self.number_of_pages = number_of_pages
        self.price_unit = price_unit
        self.author_id = author_id
        self.company_id = company_id
        self.other_books = other_books
        self.created_at = created_at or datetime.now()
        self.publication_date = publication_date or datetime.now()

    def book_details(self):
        return f"The book {self.title} is described as {self.description}, has {self.number_of_pages} pages, costs {self.price_unit}, and was published on {self.publication_date}."
