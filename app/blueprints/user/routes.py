import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.user import User
from app.models.book import Book
from email_validator import validate_email, EmailNotValidError


#Creating user Blueprint

user_bp = Blueprint("users", __name__)


#--------- USER VALIDATION HELPERS ---------

#method to validate a password

def validate_password(password):
    #rules: min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

    if re.match(pattern, password):
        return True
    
    return False

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
                
    if "password" in data:
        if not data["password"]:
            errors["password"] = "Password is required"
        
        elif not validate_password(data["password"]):
            errors["password"] = "password must contain min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char"
        
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

#Get all the users in the database

@user_bp.route("/", methods=["GET"])
@jwt_required()
def get_users():
    
    #get the user who requested the endpoint
    
    requesting_user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    requesting_user = User.query.get(requesting_user_id)
    
    if not requesting_user:
        return jsonify({"Error": "User not Found"}), 404
    
    if claims["role"].lower() != "admin":
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

#Get an user by id, protected route user must have a jwt token to access this route

@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    
    #get the user who requested the endpoint
    
    requesting_user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    requesting_user = User.query.get(requesting_user_id)
    
    if not requesting_user:
        return jsonify({"Error": "User Not Found"}), 404
    
    #if requesting user is admin then provide the user info
    
    if claims["role"].lower() == "admin":
        requested_user = User.query.get(user_id)
        
        if not requested_user:
            return jsonify({"Error": "User Not Found"}), 404
        
        return jsonify(requested_user.to_dict()), 200
    
    #if a user is not admin and is requesting details of other user block that
    
    if requesting_user.id != user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    #if a user is requesting is own details then retur the details
    
    return jsonify(requesting_user.to_dict()), 200

#Add a book to a user

@user_bp.route("/<int:user_id>/books", methods=["POST"])
@jwt_required()
def add_book_to_user(user_id):
    
    requesting_user_id = int(get_jwt_identity())
    
    requesting_user = User.query.get(requesting_user_id)
    
    if not requesting_user:
        return jsonify({"Error": "User not Found"}), 404
    
    if requesting_user_id != user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    data = request.get_json()
    errors = validate_book_create(data)
    
    if errors:
        return jsonify({"Error": "Validation failed", "Details": errors}), 400
    

    book = Book(Name=data["Name"], Author=data["Author"], user_id=user_id)
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201


#Get all the books owned by a user

@user_bp.route("/<int:user_id>/books", methods=["GET"])
@jwt_required()
def get_user_books(user_id):
    requesting_user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    requesting_user = User.query.get(requesting_user_id)
    
    
    if not requesting_user:
        return jsonify({"Error": "User Not Found"}), 404
    
    if claims["role"].lower() == "admin":
        requested_user = User.query.get(user_id)
        
        if not requested_user:
            return jsonify({"Error": "User Not Found"}), 404
        
        return jsonify([book.to_dict() for book in requested_user.books])
    
    if requesting_user_id != user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    return jsonify([book.to_dict() for book in requesting_user.books]), 200

#update user details

@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    requesting_user_id = int(get_jwt_identity())
    
    requesting_user = User.query.get(requesting_user_id)
    
    if not requesting_user:
        return jsonify({"Error": "User Not Found"}), 404
    
    if requesting_user_id != user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    data = request.get_json()
    
    errors = validate_user_update(data)
    
    if errors:
        return jsonify({"Error": "Validation Failed", "Details": errors}), 400
    
    requesting_user.first_name = data.get("first_name", requesting_user.first_name)
    requesting_user.last_name = data.get("last_name", requesting_user.last_name)
    requesting_user.email_id = data.get("email_id", requesting_user.email_id).lower()
    if "password" in data:
        requesting_user.set_password(data["password"])
    
    db.session.commit()
    
    return jsonify({"message": "User Details Updated Successfully", "Details": requesting_user.to_dict()}), 200

#Delete a user

@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    requesting_user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    requesting_user = User.query.get(requesting_user_id)
    
    if not requesting_user:
        return jsonify({"Error": "User Not Found"}), 404
    
    if claims["role"].lower() == "admin":
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"Error": "User Not Found"}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"Message": f"User with user id {user_id} is deleted successfully"}), 200
    
    if requesting_user_id != user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    db.session.delete(requesting_user)
    db.session.commit()
    
    return jsonify({"Message": f"User with user id {requesting_user_id} is deleted successfully"}), 200