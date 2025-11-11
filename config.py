# config.py
import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-hard-to-guess-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
    # --- SQL DATABASE ---
    # (This should be your existing MySQL connection string)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://inf2003-user:UCMS%40inf2003@35.212.249.216/inf2003-db'
        
    # --- NOSQL DATABASE ---
    # This is YOUR specific connection string from the sample.
    # I've added the database name 'ucms_db' at the end.
    MONGO_URI = "mongodb+srv://inf2003-admin:wRy7zbLFw7jjRGEt@cluster0.spxkjcp.mongodb.net/ucms_db?appName=Cluster0"