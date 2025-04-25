from flask import Blueprint, request, jsonify
from app.status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT,
    HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED, HTTP_200_OK, HTTP_401_UNAUTHORIZED
)
import validators
from app.Models.company_model import Company
from app.Models.author_model import Author
from app.Models.book_model import Book
from app.extensions import db, bcrypt
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, jwt_required
)
from datetime import datetime

# Book blueprint
books = Blueprint('book', __name__, url_prefix='/api/v1/books')

# Creating a book
@books.route('/create', methods=['POST'])
@jwt_required()
def createBook():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    number_of_pages = data.get('number_of_pages')
    price = data.get('price')
    price_unit = data.get('price_unit')
    publication_date = data.get('publication_date')
    other_books = data.get('other_books')
    company_id = data.get('company_id')
    created_at = data.get('created_at')
    author_id = get_jwt_identity()

    # Validations
    if not title or not number_of_pages or not description  or not price or not price_unit or not publication_date:
        return jsonify({"error": "All fields are required"}), HTTP_400_BAD_REQUEST

    if Book.query.filter_by(title=title, author_id=author_id).first() is not None:
        return jsonify({"error": "Book title and author id already in use"}), HTTP_409_CONFLICT

    try:
        # Creating a new book
        new_book = Book(
            title=title,
            number_of_pages=number_of_pages,
            description=description,
            price=price,
            price_unit=price_unit,
            publication_date=publication_date,
            other_books=other_books,
            created_at=created_at,
            company_id=company_id,
            author_id=author_id
        )
        db.session.add(new_book)
        db.session.commit()

        return jsonify({
            'message': f"{title} has been successfully created",
            'book': {
                "id": new_book.id,
                "title": new_book.title,
                "price": new_book.price,
                "description": new_book.description,
                "price_unit": new_book.price_unit,
                "number_of_pages": new_book.number_of_pages,
                "other_books": new_book.other_books,
                "created_at": new_book.created_at,
                "company": {
                    'id': new_book.company.id,
                    'name': new_book.company.name,
                    'origin': new_book.company.origin,
                    'description': new_book.company.description,
                    'created_at': new_book.company.created_at
                },
                "author": {
                    'first_name': new_book.author.first_name,
                    'last_name': new_book.author.last_name,
                    'username': new_book.author.get_full_name(),
                    'email': new_book.author.email,
                    'biography': new_book.author.biography,
                    'contact': new_book.author.contact,
                    'type': new_book.author.user_type,
                    'created_at': new_book.author.created_at
                }
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

# Getting all books
@books.get('/all')
@jwt_required()
def getAllBooks():

    try:
        all_books = Book.query.all()

        books_data = []
        for book in all_books :
            book_info ={
                "id": book.id,
                "title": book.title,
                "price": book.price,
                "description": book.description,
                "price_unit": book.price_unit,
                "number_of_pages": book.number_of_pages,
                "other_books": book.other_books,
                "created_at": book.created_at,
                "company": {
                    'id': book.company.id,
                    'name': book.company.name,
                    'origin': book.company.origin,
                    'description': book.company.description,
                    'created_at': book.company.created_at
                }},
            books_data.append(book_info)

        return jsonify({
            'message': "All books retrieved successfully",
            'total_companys': len(books_data),
            "books": books_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    
@books.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def updateBookDetails(id):
    try:
        current_author_id = get_jwt_identity()
        logged_in_author = Author.query.filter_by(id=current_author_id).first()

        # Get the book
        book = Book.query.filter_by(id=id).first()
        if not book:
            return jsonify({
                "error": "Book not found"
            }), HTTP_404_NOT_FOUND

        # Authorization check: only the author who created the book or an Admin can update
        if logged_in_author.user_type == 'Admin' and book.author_id == current_author_id:
            return jsonify({
                "error": "You are not authorized to update this book"
            }), HTTP_403_FORBIDDEN

        # Get updated data from request
        data = request.get_json()
        title = data.get('title', book.title)
        description = data.get('description', book.description)
        number_of_pages = data.get('number_of_pages', book.number_of_pages)
        price = data.get('price', book.price)
        price_unit = data.get('price_unit', book.price_unit)
        publication_date = data.get('publication_date', book.publication_date)
        other_books = data.get('other_books', book.other_books)

        # Check for unique title per author
        if title == book.title:
            if Book.query.filter_by(title=title, author_id=current_author_id).first():
                return jsonify({
                    "error": "Title already in use by this author"
                }), HTTP_409_CONFLICT

        # Update fields
        book.title = title
        book.description = description
        book.number_of_pages = number_of_pages
        book.price = price
        book.price_unit = price_unit
        book.publication_date = publication_date
        book.other_books = other_books

        db.session.commit()

        return jsonify({
            'message': f"{title} has been successfully updated",
            "book": {
                'id': book.id,
                'title': book.title,
                'description': book.description,
                'number_of_pages': book.number_of_pages,
                'price': book.price,
                'price_unit': book.price_unit,
                'publication_date': book.publication_date,
                'other_books': book.other_books,
                'created_at': book.created_at,
                'author': {
                    'first_name': book.author.first_name,
                    'last_name': book.author.last_name,
                    'email': book.author.email,
                    'authorname': book.author.get_full_name(),
                    'biography': book.author.biography,
                    'contact': book.author.contact,
                    'type': book.author.user_type,
                    'created_at': book.author.created_at,
                }
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR

# #Deletes a company
# @companys.route('/delete/<int:id>', methods =['DELETE'])
# @jwt_required()
# def deleteCompany(id):

#     try:
#         current_author = get_jwt_identity()
#         loggedInAuthor = Author.query.filter_by(id=current_author).first()

# #get company by id
#         company = Company.query.filter_by(id=id).first()

#         if not company:
#             return jsonify({
#                 "error": "Company not found"
#             }),HTTP_404_NOT_FOUND
        
#         elif loggedInAuthor.user_type == 'Admin' and company.id == current_author:
#             return jsonify({
#                 "error":"You are not authorized to delete this company."
#             }),HTTP_403_FORBIDDEN
#         else:


#             #delete associated books 
#             for book in company.books:
#                 db.session.delete(book)
            

#             db.session.delete(company)
#             db.session.commit()


#             return jsonify({
#                 'message': "Company deleted successfully",

#             })

#     except Exception as e:
#         return jsonify({
#             'error':str(e)
#         }),HTTP_500_INTERNAL_SERVER_ERROR
