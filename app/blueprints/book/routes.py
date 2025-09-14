import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.book import Book
from app.models.user import User

#creating book blueprint

book_bp = Blueprint("books", __name__)


#---------- VALIDATION HELPERS -----------


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


#----------- API ENDPOINTS RELATED TO BOOK ------------

#Get all the books, [Also Enhanced now with Paging and Filtering]

@book_bp.route("/", methods=["GET"])
@jwt_required()
def get_books():
    
    requesting_user_id = int(get_jwt_identity())
    requesting_user = User.query.get(requesting_user_id)
    claims = get_jwt()
    
    if not requesting_user:
        return jsonify({"Error": "User not Found"}), 404
    
    if claims["role"].lower() != "admin":
        return jsonify({"Error": "Unauthorized Access"}), 403
    
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
    }), 200

#Get a book by id

@book_bp.route("/<int:book_id>", methods=["GET"])
@jwt_required()
def get_book(book_id):
    
    requesting_user_id = int(get_jwt_identity())
    requesting_user = User.query.get(requesting_user_id)
    claims = get_jwt()
    
    if not requesting_user:
        return jsonify({"Error": "User Not Found"}), 404
    
    if claims["role"].lower() == "admin":
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({"Error": "Book Not Found"}), 404
        
        return jsonify(book.to_dict()), 200
    
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"Error": "Book Not Found"}), 404
    
    if requesting_user_id != book.user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    return jsonify(book.to_dict()), 200
    
    


#update Name and Author of a book

@book_bp.route("/<int:book_id>", methods=["PUT"])
@jwt_required()
def update_book(book_id):
    requesting_user_id = int(get_jwt_identity())
    requesting_user = User.query.get(requesting_user_id)
    
    if not requesting_user:
        return jsonify({"Error": "User Not Found"}), 404
    
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"Error": "Book Not Found"}), 404
    
    if book.user_id != requesting_user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    data = request.get_json()
    errors = validate_book_update(data)
    
    if errors:
        return jsonify({"Error": "Validation Failed", "Details": errors}), 400
    
    book.Name = data.get("Name", book.Name)
    book.Author = data.get("Author", book.Author)
    
    db.session.commit()
            
    return jsonify({"Message": "Book Details Updated Successfully", "Details": book.to_dict()}), 200


#delete a book by it's id        
    

@book_bp.route("/<int:book_id>", methods=["DELETE"])
@jwt_required()
def delete_book(book_id):
    requesting_user_id = int(get_jwt_identity())
    requesting_user = User.query.get(requesting_user_id)
    claims = get_jwt()
    
    if not requesting_user:
        return jsonify({"Error": "User Not Found"}), 404
    
    if claims["role"].lower() == "admin":
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({"Error": "Book Not Found"}), 404
        
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({"Message": f"Book with book id {book_id} deleted successfully"}), 200
    
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"Error": "Book Not Found"}), 404
    
    if requesting_user_id != book.user_id:
        return jsonify({"Error": "Unauthorized Access"}), 403
    
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({"Message": f"Book with book id {book_id} deleted succesfully"}), 200