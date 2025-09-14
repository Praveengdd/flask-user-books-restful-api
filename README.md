# 📚 Flask Books API

A RESTful API built with **Flask** and **SQLAlchemy**, using **MySQL** as the database.  
This API manages **Users** and their **Books** with a one-to-many relationship:
- A **User** can own multiple **Books**
- A **Book** belongs to a single **User**

---

## 🚀 Features
- Registration and Login for Users
- Protected route to access user by id
- update user details
- delete an user
- Add books for a specific user
- Fetch all books or only books owned by a particular user
- Fetch Books based on filtering
- Fetch Books by doing pagination
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
- `POST /register` → User Registration
- `POST /login` → User Login   
- `GET /users` → Get all users (protected only for admin)
- `GET /users/<id>` → Get a single user by ID (protected route)
- `PUT /users/<id>` → Update details of a user by ID (protected for users, only users can update their details)
- `DELETE /users/<id>` → Delete a user by ID (protected for admin and users, user can only delete themselves)

### Books (User-specific)
- `POST /users/<id>/books` → Add a new book for a user (protected only for user)
- `GET /users/<id>/books` → Get all books owned by a user  (protected for admin and user)

### Books (Global)
- `GET /books` → Get all books (protected only for admin)
- `GET /books/<id>` → Get a single book by ID (protected for admin and user)
- `PUT /books/<id>` → Update a book (title, author)  (protected only for admin)
- `DELETE /books/<id>` → Delete a book  (protected for user and admin)

---

## Steps Completed

✅ Implemented CRUD + relationships

✅ Validation and error handling (API Design Advancement)

✅ Pagination and Filtering (API Design Advancement)

✅ Add authentication (JWT-based login/signup)

🔜 Deploy to cloud (Render/Heroku/AWS)



## ✍️ Author: Praveen Kumar G D



