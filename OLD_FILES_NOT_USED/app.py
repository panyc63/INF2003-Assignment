# import json
# from flask import Flask
# from website.models import db

# # this import not needed after using mysql server
# # from services.services import initialize_database
# from config import DevelopmentConfig   
# from website.routes.views import views_bp
# from website.routes.api import api_bp


# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# uri = "mongodb+srv://inf2003-admin:wRy7zbLFw7jjRGEt@cluster0.spxkjcp.mongodb.net/?appName=Cluster0"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
# # Initialize Flask app
# app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ucms.db']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TYKroot%40321@localhost/inf2003-db'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:PASSWORD@localhost/inf2003-db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = 'super_secret_key' 
# db.init_app(app)


# app.register_blueprint(views_bp)
# app.register_blueprint(api_bp)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         # initialize_database()
        
#     app.run(debug=True, port=5000)