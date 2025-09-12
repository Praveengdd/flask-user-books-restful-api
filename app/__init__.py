from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.errors import register_error_handlers



db = SQLAlchemy()
migrate = Migrate()

from app.models.user import User
from app.models.book import Book


def create_app():
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    app.config.from_pyfile("config.py", silent=True)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.blueprints.book.routes import book_bp
    from app.blueprints.user.routes import user_bp
    
    
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(book_bp, url_prefix="/books")
    register_error_handlers(app)
    
    return app