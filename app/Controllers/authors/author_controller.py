from flask import Blueprint,request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK
import validators
from app.Models.author_model import Author
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity,  jwt_required

#authors blueprint
author = Blueprint('author', __name__,url_prefix= '/api/v1/author')


# #Getting all authors from the database
# @author.get('/')
# @jwt_required()
# def getAllAuthors():

    # email = request.json.get('email')
    # password = request.json.get('password')

    # try:

    #     all_authors = Author.query.all() # Please serilaize the data by converting it into json
    #     authors_data = []

    #     for author in all_authors:
    #         author_info ={
    #             'id': author.id,
    #             'first_name':author.first_name,
    #             'last_name':author.last_name,
    #             'username':author.get_full_name(),
    #             'email': author.email,
    #             'contact': author.contact,
    #             'type':author.user_type,
    #             'created_at': author.created_at
    #         }
    #         authors_data.append(author_info)

    #     return jsonify({

    #         'message': "All authors retrieved succesfully",
    #         'total_authors': len(authors_data),
    #         'users': authors_data
    #     }), HTTP_200_OK
        
        
    # except Exception as e:
    #     return jsonify({
    #         'error':str(e)
    #     }),HTTP_500_INTERNAL_SERVER_ERROR


@author.get('/author')
@jwt_required()
def get_authors():

    # email = request.json.get('email')
    # password = request.json.get('password')

    try:

        all_authors = Author.query.filter_by(user_type = 'author').all()
        authors_data = []

        for author in all_authors:
            author_info ={
                'id': author.id,
                'first_name':author.first_name,
                'last_name':author.last_name,
                'username':author.get_full_name(),
                'email': author.email,
                'contact': author.contact,
                # 'biography':author.biography,
                'created_at': author.created_at,
                'companys': [],
                'books':[],

            }
            if hasattr(author,'books'):
                author_info['books'] = [{
                    'id': book.id,
                    'title':book.title,
                    'price': book.price,
                    'price_unit':book.price_unit,
                    'description': book.description,
                    'publication_date': book.publication_date,
                    'created_at': book.created_at
                } for book in author.books]
            
            if hasattr(author, 'companys'):
                author_info['companys'] = [{
                    'id':company.id,
                    'name': company.name,
                    'origin': company.origin
                } for company in author.companys]

            authors_data.append(author_info)

        return jsonify({

            "message": 'All authors retrieved succesfully',
            'total': len(authors_data),
            'authors': authors_data
        }), HTTP_200_OK
        
        
    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR

