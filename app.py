import json
from flask import Flask
from models import db
from services import initialize_database

from routes.views import views_bp
from routes.api import api_bp

# Initialize Flask app
app = Flask(__name__, template_folder='website', static_folder='website/static')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ucms.db']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TYKroot%40321@localhost/inf2003-db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:PASSWORD@localhost/inf2003-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_key' 
db.init_app(app)

app.register_blueprint(views_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # initialize_database()
        
    app.run(debug=True, port=5000)