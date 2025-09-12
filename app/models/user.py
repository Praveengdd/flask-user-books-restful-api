from app import db
from werkzeug.security import check_password_hash, generate_password_hash

#User Model

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(25), nullable=False, default="user")
    
    #One to many relationship between user and books
    books = db.relationship('Book', backref='owner', lazy=True, passive_deletes=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def to_dict(self):
        return {"id": self.id, "Name": self.first_name + " " + self.last_name, "email_id": self.email_id, "role": self.role, "books": [book.id for book in self.books]}