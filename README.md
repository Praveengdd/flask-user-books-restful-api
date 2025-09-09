# 📚 Flask Books API

A RESTful API built with **Flask** and **SQLAlchemy**, using **MySQL** as the database.  
This API manages **Users** and their **Books** with a one-to-many relationship:
- A **User** can own multiple **Books**
- A **Book** belongs to a single **User**

---

## 🚀 Features
- Add and retrieve users
- Add books for a specific user
- Fetch all books or only books owned by a particular user
- Update or delete a book
- Persistent storage with MySQL

---

## 🛠️ Tech Stack
- **Flask** (Python web framework)
- **Flask-SQLAlchemy** (ORM)
- **MySQL** (database)
- **Postman** (API testing)

---

## 📌 API Endpoints

### Users
- `POST /users` → Create a new user  
- `GET /users` → Get all users  
- `GET /users/<id>` → Get a single user by ID  

### Books (User-specific)
- `POST /users/<id>/books` → Add a new book for a user  
- `GET /users/<id>/books` → Get all books owned by a user  

### Books (Global)
- `GET /books` → Get all books  
- `GET /books/<id>` → Get a single book by ID  
- `PUT /books/<id>` → Update a book (title, author, or reassign to another user)  
- `DELETE /books/<id>` → Delete a book  

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/flask-books-api.git
cd flask-books-api
```
### 2. Install dependencies
```python
pip install flask flask-sqlalchemy mysqlclient
```

### 3. Create a MySQL database
Log into MySQL and create a database:
```sql
CREATE DATABASE booksdb;
```

### 4. Configure database connection
In app.py, update this line with your credentials:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/booksdb'
```
### 5. Run the app
```python
python app.py
```
The API will be available at:
👉 http://127.0.0.1:5000/

## 🧪 Testing

Use Postman
 to test the endpoints.

Example request (Add a user):
```http
POST /users
Content-Type: application/json

{
  "name": "Praveen"
}
```

Example request (Add a book to user 1):
```http
POST /users/1/books
Content-Type: application/json

{
  "title": "Flask for Beginners",
  "author": "John Doe"
}
```

## Steps Completed

✅ Implemented CRUD + relationships

🔜 Add authentication (JWT-based login/signup)

🔜 Advanced API design (validation, pagination, error handling)

🔜 Deploy to cloud (Render/Heroku/AWS)




## ✍️ Author: Praveen Kumar G D



