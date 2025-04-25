from flask import Blueprint,request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST,HTTP_404_NOT_FOUND, HTTP_409_CONFLICT,HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_200_OK,HTTP_401_UNAUTHORIZED
import validators
from app.Models.company_model import Company
from app.Models.author_model import Author
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity,  jwt_required

#Company blueprint
companys = Blueprint('company', __name__,url_prefix= '/api/v1/companys')


#Creating companys
@companys.route('/create' , methods=['POST'])
@jwt_required()
def createCompany():

    #Storing request values
    data = request.json
    origin = data.get('origin')
    description = data.get('description')
    company_id = get_jwt_identity()
    name = data.get('name')
    location = data.get('location')


#Validations of the incoming request.
    if not name or not origin or not description or not location:
        return({"error":"All fields are required"}),HTTP_400_BAD_REQUEST
    
    if Company.query.filter_by(name=name).first() is not None:
        return({"error":"Company name already in use"}),HTTP_409_CONFLICT
    
    try:

        #Creating a new company
        new_company = Company(
            name=name, origin=origin, description=description, location=location, company_id=company_id
        )
        db.session.add(new_company)
        db.session.commit()

        return({
            'message': name + " has been created succesfully created ",
            'company':{
                "id":new_company.id,
                "name":new_company.name,
                "origin":new_company.origin,
                "description":new_company.description,
                "location":new_company.location
            }
        }),HTTP_201_CREATED


    except Exception as e:
        db.session.rollback()
        return jsonify ({"error":str(e)}),HTTP_500_INTERNAL_SERVER_ERROR
    
# Getting all companys
@companys.get('/all')
@jwt_required()
def getAllCompanys():

    try:
        all_companys = Company.query.all()

        companys_data = []
        for company in all_companys :
            company_info = {
                'id': company.id,
                'name': company.name,
                'origin': company.origin,
                'description': company.description,
                'author':{
                    'first_name':company.author.first_name,
                    'last_name':company.author.last_name,
                    'email':company.author.email,
                    'authorname':company.author.get_full_name(),
                    'biography': company.author.biography,
                    'contact': company.author.contact,
                    'type': company.author.user_type,
                    'created_at':company.author.created_at,
                },
                'created_at':company.created_at

                
            }
            companys_data.append(company_info)

        return jsonify({
            'message': "All companys retrieved successfully",
            'total_companys': len(companys_data),
            "companys": companys_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
    
# Getting company by id

@companys.get('/company/<int:id>')
@jwt_required()
def getCompany(id):
    try:
        company = Company.query.filter_by(id=id).first()

        if not company:
            return jsonify({
                "error": "Company is not found"
            }), HTTP_404_NOT_FOUND

        return jsonify({
            'message': "Company details retrieved successfully",
            "company": {
                'id': company.id,
                'name': company.name,
                'origin': company.origin,
                'description': company.description,
                'author': {
                    'first_name': company.author.first_name,
                    'last_name': company.author.last_name,
                    'email': company.author.email,
                    'authorname': company.author.get_full_name(),
                    'biography': company.author.biography,
                    'contact': company.author.contact,
                    'type': company.author.user_type,
                    'created_at': company.author.created_at,
                },
                'created_at': company.created_at
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR

#Updates company details

@companys.route('/edit/<int:id>', methods =['PUT','PATCH'])
@jwt_required()
def updateCompanyDetails(id):

    try:
        current_author = get_jwt_identity()
        loggedInAuthor = Author.query.filter_by(id=current_author).first()

#get company by id
        company = Company.query.filter_by(id=id).first()

        if not company:
            return jsonify({
                "error": "company is not found"
            }),HTTP_404_NOT_FOUND
        
        elif loggedInAuthor.user_type == 'Admin' and company.id == current_author:
            return jsonify({
                "error":"You are not authorized to update the author details"
            }), HTTP_403_FORBIDDEN
        
        else:
            name = request.get_json().get('name',company.name)
            origin = request.get_json().get('origin',company.origin)
            description = request.get_json().get('description',company.description)
            location = request.get_json().get('location',company.location)


            if name != company.name and Company.query.filter(Company.name == name).first():
              return jsonify({
                "error": "name already in use"
              }), HTTP_409_CONFLICT


            company.name = name
            company.origin = origin
            company.description = description
            company.location = location

            db.session.commit()
            
            return jsonify({
                'message': name + "'s details have been sucessfully updated ",
            "company": {
                'id': company.id,
                'name': company.name,
                'origin': company.origin,
                'description': company.description,
                'author': {
                    'first_name': company.author.first_name,
                    'last_name': company.author.last_name,
                    'email': company.author.email,
                    'authorname': company.author.get_full_name(),
                    'biography': company.author.biography,
                    'contact': company.author.contact,
                    'type': company.author.user_type,
                    'created_at': company.author.created_at,
                },
                'created_at': company.created_at
            }
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#Deletes a company
@companys.route('/delete/<int:id>', methods =['DELETE'])
@jwt_required()
def deleteCompany(id):

    try:
        current_author = get_jwt_identity()
        loggedInAuthor = Author.query.filter_by(id=current_author).first()

#get company by id
        company = Company.query.filter_by(id=id).first()

        if not company:
            return jsonify({
                "error": "Company not found"
            }),HTTP_404_NOT_FOUND
        
        elif loggedInAuthor.user_type == 'Admin' and company.id == current_author:
            return jsonify({
                "error":"You are not authorized to delete this company."
            }),HTTP_403_FORBIDDEN
        else:


            #delete associated books 
            for book in company.books:
                db.session.delete(book)
            

            db.session.delete(company)
            db.session.commit()


            return jsonify({
                'message': "Company deleted successfully",

            })

    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR
