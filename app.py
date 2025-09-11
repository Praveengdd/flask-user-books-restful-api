import os
import re
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from email_validator import validate_email, EmailNotValidError

load_dotenv()


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#------------ DATABASE MODELS --------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(150), nullable=False, unique=True)
    
    #One to many relationship between user and books
    books = db.relationship('Book', backref='owner', lazy=True, passive_deletes=True)
    
    def to_dict(self):
        return {"id": self.id, "Name": self.first_name + " " + self.last_name, "email_id": self.email_id, "books": [book.id for book in self.books]}


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    def to_dict(self):
        return {"id": self.id, "Name": self.Name, "Author": self.Author, "user_id": self.user_id}


with app.app_context():
    db.create_all()
    
    
#------------------- VALIDATION HELPERS -------------------

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
    

#method to validate an updated book    

def validate_book_update(data):
    
    errors = {}
    
    name_pattern = re.compile(r"^[A-Za-z ]+$")
    
    if not data:
        errors["data"] = "Book data is required"
        return errors
    
    #Name
    if "Name" in data:
        if not data["Name"]:
            errors["Name"] = "Book name is required"
            
        elif len(data["Name"]) < 2:
            errors["Name"] = "Book name must be atleast 2 characters long"
        
        elif len(data["Name"]) > 255:
            errors["Name"] = "Book name must not exceed 255 characters"
        
    #Author
    if "Author" in data:
        if not data["Author"]:
            errors["Author"] = "Author name is required"
            
        elif not name_pattern.match(data["Author"]):
            errors["Author"] = "Author name must contain only alphabets and spaces"
            
            
    return errors        
    
    
    
#------------------- API ROUTES/ENDPOINTS -----------------
    
#Add an user to the database
    
@app.route("/users", methods=["POST"])
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

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

#Get an user by id

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error": "User Not Found"}), 404
    
    return jsonify(user.to_dict())

#Add a book to a user

@app.route("/users/<int:user_id>/books", methods=["POST"])
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

@app.route("/users/<int:user_id>/books", methods=["GET"])
def get_user_books(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error": "User Not Found"}), 404
    
    return jsonify([book.to_dict() for book in user.books])


#update user details

@app.route("/users/<int:user_id>", methods=["PUT"])
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

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error": "User Not Found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"Message": f"User with user id {user_id} is deleted successfully"})
    


#Get all the books, [Also Enhanced now with Paging and Filtering]

@app.route("/books", methods=["GET"])
def get_books():
    
    #filtering
    
    query = Book.query
    author = request.args.get("Author")
    name = request.args.get("Name")
    user_id = request.args.get("user_id")
    
    if author:
        query = query.filter(Book.Author.like(f"%{author}%"))
    if name:
        query = query.filter(Book.Name.like(f"%{name}%"))
    if user_id:
        query = query.filter_by(user_id=user_id)
        
    #pagination
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    paginated = query.paginate(page=page, per_page=limit, error_out=False)
    
    books = [book.to_dict() for book in paginated.items]
    
    
    return jsonify({
        "page": page,
        "limit": limit,
        "total": paginated.total,
        "total pages": paginated.pages,
        "books": books
    })

#Get a book by id

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_dict())
    
    return jsonify({"Error": "Book Not Found"}), 404


#update Name and Author of a book

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"Error": "Book Not Found"}), 404
    
    data = request.get_json()
    errors = validate_book_update(data)
    
    if errors:
        return jsonify({"Error": "Validation Failed", "Details": errors})
    
    book.Name = data.get("Name", book.Name)
    book.Author = data.get("Author", book.Author)
    
    db.session.commit()
            
    return jsonify(book.to_dict())


#delete a book by it's id        
    

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"Error": "Book Not Found"}), 404
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({"message": f"Book with book id {book_id} deleted succesfully"})



#-------------- CUSTOM ERROR HANDLERS ------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({"Error" : "Resource Not Found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"Error": "Something went wrong"}), 500
    

#-------------- API ENTRYPOINT -------------------

if __name__ == "__main__":
    app.run(debug=True)