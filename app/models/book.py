from app import db

#Book Model

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    def to_dict(self):
        return {"id": self.id, "Name": self.Name, "Author": self.Author, "user_id": self.user_id}