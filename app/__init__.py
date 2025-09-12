from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.errors import register_error_handlers



db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

from app.models.user import User
from app.models.book import Book


def create_app():
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    app.config.from_pyfile("config.py", silent=True)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    from app.blueprints.book.routes import book_bp
    from app.blueprints.user.routes import user_bp
    from app.blueprints.auth.routes import auth_bp
    
    
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(book_bp, url_prefix="/books")
    app.register_blueprint(auth_bp)
    register_error_handlers(app)
    
    return app