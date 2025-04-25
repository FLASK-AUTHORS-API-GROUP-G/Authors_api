from flask import Blueprint,request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK, HTTP_403_FORBIDDEN
import validators
from app.extensions import db ,bcrypt
from app.Models.author_model import Author
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity,  jwt_required
from sqlalchemy import or_, and_

#Authors blueprint
authors = Blueprint('authors', __name__,url_prefix= '/api/v1/authors')


# Getting all authors from the datbase
@authors.get('/all')
def getAllAuthors():

    try:
        all_authors = Author.query.all()

        authors_data = []
        for author in all_authors :
            author_info = {
                'id': author.id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'username':author.get_full_name(),
                'email': author.email,
                'biography': author.biography,
                'contact': author.contact,
                'type': author.user_type,
                'created_at':author.created_at
            }
            authors_data.append(author_info)

        return jsonify({
            'message': "All users retrieved successfully",
            'total_authors': len(authors_data),
            "authors": authors_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    INTERNAL_SERVER_ERROR

# Getting an author by id

@authors.get('/author/<int:id>')
@jwt_required()
def getAuthor(id):

    try:
        author = Author.query.filter_by(id = id).first()

        if not author:
            return jsonify({
                "error": "Author not found"
            }),HTTP_404_NOT_FOUND
        

        books =[]
        companys = []


        if hasattr(author, 'books'):
            books = [{
                'id' : book.id,
                'title': book.title,
                'price': book.price,
                'genre': book.genre,
                'price_unit':book.price_unit,
                'description': book.description,
                'publication': book.publication_date,
                'image': book.image,
                'created_at':book.created_at
            } for book in author.books]

        if hasattr (author, 'companys'):
            companys = [{
                'id':company.id,
                'name': company.name,
                'origin': company.origin,
                'description': company.description
            } for company in author.companys]
        return jsonify({
            'message': "Author details retrieved successfully",
            "authors": {
                'id': author.id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'username':author.get_full_name(),
                'email': author.email,
                'contact': author.contact,
                'type': author.user_type,
                'biography': author.biography,
                'created_at':author.created_at,
                'companys':companys,
                'books':books
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR

# Update author details

@authors.route('/edit/<int:id>', methods =['PUT','PATCH'])
@jwt_required()
def updateAuthorDetails(id):

    try:
        current_author = get_jwt_identity()
        loggedInAuthor = Author.query.filter_by(id=current_author).first()

#get author by id
        author = Author.query.filter_by(id=id).first()

        if not author:
            return jsonify({
                "error": "Author not found"
            }),HTTP_404_NOT_FOUND
        
        elif loggedInAuthor.user_type == 'Admin' and author.id == current_author:
            return jsonify({
                "error":"You are not authorized to update the author details"
            })
        else:
            first_name = request.get_json().get('first_name',author.first_name)
            last_name = request.get_json().get('last_name',author.last_name)
            email = request.get_json().get('email',author.email)
            contact = request.get_json().get('contact',author.contact)
            biography = request.get_json().get('biography',author.biography)
            user_type = request.get_json().get('user_type',author.user_type)

            if "password" in request.json:
                hashed_password = bcrypt.generate_password_hash(request.json.get('password'))
                author.password = hashed_password

            # if email != author.email and Author.query.filter_by(email=email).first():
            #     return jsonify({
            #         "error": "Email Address already in use"
            #     }),HTTP_409_CONFLICT
            
            # if contact != author.contact and Author.query.filter_by(contact=contact).first():
            #     return jsonify({
            #         "error": "Contact already in use"
            #     }),HTTP_409_CONFLICT
            if email != author.email and Author.query.filter(Author.email == email, Author.id != author.id).first():
                 return jsonify({
                    "error": "Email Address already in use"
                 }), HTTP_409_CONFLICT

            if contact != author.contact and Author.query.filter(Author.contact == contact, Author.id != author.id).first():
              return jsonify({
                "error": "Contact already in use"
              }), HTTP_409_CONFLICT


            author.first_name = first_name
            author.last_name = last_name
            author.email = email
            author.contact = contact
            author.biography = biography
            author.user_type = user_type

            db.session.commit()
            
            user_name = author.get_full_name()

            return jsonify({
                'message': user_name + "'s details have been sucessfully updated ",
                'author':{
                'id': author.id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'email': author.email,
                'contact': author.contact,
                'type': author.user_type,
                'biography':author.biography,
                'updated_at':author.updated_at,
                }
            })


    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


# Delete an author
@authors.route('/delete/<int:id>', methods =['DELETE'])
@jwt_required()
def deleteAuthor(id):

    try:
        current_author = get_jwt_identity()
        loggedInAuthor = Author.query.filter_by(id=current_author).first()

#get author by id
        author = Author.query.filter_by(id=id).first()

        if not author:
            return jsonify({
                "error": "Author not found"
            }),HTTP_404_NOT_FOUND
        
        elif loggedInAuthor.user_type == 'Admin' and author.id == current_author:
            return jsonify({
                "error":"You are not authorized to delete this author."
            }),HTTP_403_FORBIDDEN
        else:


            #delete associated companies 
            for company in author.companys:
                db.session.delete(company)
            
            #delete associated books 
            for book in author.books:
                db.session.delete(book)

            db.session.delete(author)
            db.session.commit()


            return jsonify({
                'message': "Author deleted successfully",

            })


    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR

# # Search for authors

from sqlalchemy import or_, and_

# Search for authors
@authors.get('/search')
def searchAuthors():
    try:
        search_query = request.args.get('query', '')

        # Using their first or last name and filtering by user_type = 'author'
        authors = Author.query.filter(
            and_(
                or_(
                    Author.first_name.ilike(f"%{search_query}%"),
                    Author.last_name.ilike(f"%{search_query}%")
                ),
                Author.user_type == 'author'
            )
        ).all()

        if len(authors) == 0:
            return jsonify({
                'message': "No results found"
            }), HTTP_404_NOT_FOUND

        authors_data = []
        for author in authors:
            author_info = {
                'id': author.id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'username': author.get_full_name(),
                'email': author.email,
                'biography': author.biography,
                'contact': author.contact,
                'type': author.user_type,
                'created_at': author.created_at
            }
            authors_data.append(author_info)

        return jsonify({
            'message': f"Authors with name '{search_query}' retrieved successfully",
            'total_search': len(authors_data),
            "search_results": authors_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
