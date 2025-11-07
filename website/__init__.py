# website/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from config import DevelopmentConfig

# 1. Initialize extensions (unbound)
db = SQLAlchemy()
mongo = PyMongo()

def create_app(config_class=DevelopmentConfig):
    """Creates and configures the Flask app."""
    
    # We use 'website.templates' and 'website.static'
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # 2. Load configuration
    app.config.from_object(config_class)

    # 3. Connect extensions to the app
    db.init_app(app)
    mongo.init_app(app)

    # 4. Register Blueprints (routes)
    # Use relative imports '.' to import from the current package
    from .routes.views import views_bp
    from .routes.api import api_bp
    
    app.register_blueprint(views_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')

    # 5. Create SQL tables if they don't exist
    with app.app_context():
        db.create_all()

    print("Flask app created and databases initialized.")
    return app