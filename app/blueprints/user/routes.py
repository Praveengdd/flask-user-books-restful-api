import re
from flask import Blueprint, jsonify, request
from app import db
from app.models.user import User
from app.models.book import Book
from email_validator import validate_email, EmailNotValidError


#Creating user Blueprint

user_bp = Blueprint("users", __name__)


#--------- USER VALIDATION HELPERS ---------

#method to validate an user

def validate_user_create(data):
    errors = {}
    
    name_pattern = re.compile(r"^[A-Za-z ]+$")
    
    if not data:
        errors["data"] = "User data is required"
        return errors
    
    #first_name
    
    if "first_name" not in data or not data["first_name"]:
        errors["first_name"] = "First name is required"
        
    elif not name_pattern.match(data["first_name"]):
        errors["first_name"] = "First name should only contain alphabets and spaces"
        
    #last_name
        
    if "last_name" not in data or not data["last_name"]:
        errors["last_name"] = "Last name is required"
        
    elif not name_pattern.match(data["last_name"]):
        errors["last_name"] = "Last name should only contain alphabets and spaces"
        
    #email
    
    if "email_id" not in data or not data["email_id"]:
        errors["email_id"] = "email id is required"
    
    else:
        try:
            validate_email(data["email_id"])
        except EmailNotValidError as e:
            errors["email_id"] = str(e)
        
    return errors

#method to validate user update information

def validate_user_update(data):
    errors = {}
    
    name_pattern = re.compile(r"^[A-Za-z ]+$")
    
    if not data:
        errors["data"] = "User data is required"
        return errors
    
    #first_name
    if "first_name" in data:
        if not data["first_name"]:
            errors["first_name"] = "First name is required"
            
        elif not name_pattern.match(data["first_name"]):
            errors["first_name"] = "First name should only contain alphabets and spaces"
        
    #last_name
    if "last_name" in data:
        if not data["last_name"]:
            errors["last_name"] = "Last name is required"
            
        elif not name_pattern.match(data["last_name"]):
            errors["last_name"] = "Last name should only contain alphabets and spaces"
        
    #email
    if "email_id" in data:
        if not data["email_id"]:
            errors["email_id"] = "email id is required"
        
        else:
            try:
                validate_email(data["email_id"])
            except EmailNotValidError as e:
                errors["email_id"] = str(e)
        
    return errors


#method to validate a book

def validate_book_create(data):
    
    errors = {}
    
    name_pattern = re.compile(r"^[A-Za-z ]+$")
    
    if not data:
        errors["data"] = "Book data is required"
        return errors
    
    #Name
    
    if "Name" not in data or not data["Name"]:
        errors["Name"] = "Book name is required"
        
    elif len(data["Name"]) < 2:
        errors["Name"] = "Book name must be atleast 2 characters long"
    
    elif len(data["Name"]) > 255:
        errors["Name"] = "Book name must not exceed 255 characters"
        
    #Author
    
    if "Author" not in data or not data["Author"]:
        errors["Author"] = "Author name is required"
        
    elif not name_pattern.match(data["Author"]):
        errors["Author"] = "Author name must contain only alphabets and spaces"
        
    return errors


#--------- API USER ENDPOINTS ------------


#Add an user to the database
    
@user_bp.route("/", methods=["POST"])
def add_user():
    data = request.get_json()
    
    errors = validate_user_create(data)
    
    if errors:
        return jsonify({"Error": "Validation failed", "Details": errors}), 400
    
    
    user = User(first_name = data["first_name"], 
                last_name = data["last_name"], 
                email_id = data["email_id"])
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

#Get all the users in the database

@user_bp.route("/", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

#Get an user by id

@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error": "User Not Found"}), 404
    
    return jsonify(user.to_dict())

#Add a book to a user

@user_bp.route("/<int:user_id>/books", methods=["POST"])
def add_book_to_user(user_id):
    
    data = request.get_json()
    errors = validate_book_create(data)
    
    if errors:
        return jsonify({"Error": "Validation failed", "Details": errors}), 400
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error" : "User Not Found"}), 404
    

    book = Book(Name=data["Name"], Author=data["Author"], user_id=user.id)
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201


#Get all the books owned by a user

@user_bp.route("/<int:user_id>/books", methods=["GET"])
def get_user_books(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error": "User Not Found"}), 404
    
    return jsonify([book.to_dict() for book in user.books])


#update user details

@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error": "User Not Found"}), 404
    
    data = request.get_json()
    
    errors = validate_user_update(data)
    
    if errors:
        return jsonify({"Error": "Validation Failed", "Details": errors}), 400
    
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.email_id = data.get("email_id", user.email_id)
    
    db.session.commit()
    
    return jsonify(user.to_dict())

#Delete a user

@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error": "User Not Found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"Message": f"User with user id {user_id} is deleted successfully"})