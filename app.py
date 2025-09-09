import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

load_dotenv()


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(150), nullable=False, unique=True)
    
    #One to many relationship between user and books
    books = db.relationship('Book', backref='owner', lazy=True)
    
    def to_dict(self):
        return {"id": self.id, "Name": self.first_name + " " + self.last_name, "email_id": self.email_id, "books": [book.id for book in self.books]}


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        return {"id": self.id, "Name": self.Name, "Author": self.Author, "user_id": self.user_id}


with app.app_context():
    db.create_all()
    
#Add an user to the database
    
@app.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()
    
    if not data or "first_name" not in data or "last_name" not in data or "email_id" not in data:
        return jsonify({"Error": "first name, last name and email id are required"}), 404
    
    user = User(first_name = data["first_name"], last_name = data["last_name"], email_id = data["email_id"])
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
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"Error" : "User Not Found"}), 404
    
    data = request.get_json()
    
    if not data or "Name" not in data or "Author" not in data:
        return jsonify({"Error": "Name and Author are required"}), 404
    
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

#Get all the books

@app.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    
    return jsonify([book.to_dict() for book in books])

#Get a book by id

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify(book.to_dict())
    
    return jsonify({"Error": "Book Not Found"}), 404


#update Name, Author and User of a book

@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"Error": "Book Not Found"}), 404
    
    data = request.get_json()
    
    book.Name = data.get("Name", book.Name)
    book.Author = data.get("Author", book.Author)
    
    #If you want to change the owner of the book
    
    book.user_id = data.get("user_id", book.user_id)
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
    



if __name__ == "__main__":
    app.run(debug=True)