import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from email_validator import validate_email, EmailNotValidError
from app import db
from app.models.user import User

#Creating auth Blueprint

auth_bp = Blueprint("auth", __name__)

#--------- VALIDATION HELPERS ---------

#method to validate a password

def validate_password(password):
    #rules: min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

    if re.match(pattern, password):
        return True
    
    return False


#method to validate a user

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
            
    #password
    
    if "password" not in data or not data["password"]:
        errors["password"] = "Password is required"
        
    elif not validate_password(data["password"]):
        errors["password"] = "password must contain min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char"
        
    #role
        
    if "role" in data:
        if not data["role"]:
            errors["role"] = "Invalid role"
        if data["role"].lower() != "admin" and data["role"].lower() != "user":
            errors["role"] = "Invalid role"
            
            
    return errors

#method to validate user login credentials
def validate_credentials(data):
    
    errors = {}
    
    if not data:
        errors["data"] = "Credentials are required"
        return errors
    
    #email id
    
    if "email_id" not in data or not data["email_id"]:
        errors["email_id"] = "Email Id is required"
        
    else:
        try:
            validate_email(data["email_id"])
        except EmailNotValidError as e:
            errors["email_id"] = str(e)
            
    #password
    
    if "password" not in data or not data["password"]:
        errors["password"] = "Password is required"
        
    elif not validate_password(data["password"]):
        errors["password"] = "password must contain min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit, 1 special char"

    
    return errors

#-------------- API ENDPOINTS ----------------


#route for a user to register

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    errors = validate_user_create(data)
    
    if errors:
        return jsonify({"Error": "Validation Failed", "Details": errors}), 400
    
    existing_user = User.query.filter_by(email_id=data["email_id"].lower()).first()
    
    if existing_user:
        return jsonify({"Error": "Email Already Exists"}), 409
    
    user = User(first_name=data["first_name"],
                last_name=data["last_name"],
                email_id=data["email_id"].lower())
    
    user.set_password(data["password"])
    
    if "role" in data:
        user.role = data["role"].lower()
        
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"Message":"User Registered Successfully", 
                    "Details": user.to_dict()}), 201
    
    
#route for user to login, also jwt tokens for user are created here

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    errors = validate_credentials(data)
    
    if errors:
        return jsonify({"Error": "Validation Failed", "Details": errors}), 400
    
    existing_user = User.query.filter_by(email_id=data["email_id"].lower()).first()
    
    if not existing_user or not existing_user.check_password(data["password"]):
        return jsonify({"Error": "Invalid username or password"}), 401
    
    
    #access token and refresh token creation
    #remember identity must contain which can be casted to string
    
    access_token = create_access_token(identity=str(existing_user.id), additional_claims={"role": existing_user.role})
    refresh_token = create_refresh_token(identity=str(existing_user.id), additional_claims={"role": existing_user.role})
    
    
    return jsonify({
        "message": "Logged in Successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200
    
    
    
    
    