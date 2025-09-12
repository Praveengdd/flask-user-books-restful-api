from app import db

#User Model

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email_id = db.Column(db.String(150), nullable=False, unique=True)
    
    #One to many relationship between user and books
    books = db.relationship('Book', backref='owner', lazy=True, passive_deletes=True)
    
    def to_dict(self):
        return {"id": self.id, "Name": self.first_name + " " + self.last_name, "email_id": self.email_id, "books": [book.id for book in self.books]}