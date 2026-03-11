# config.py
import os

class Config:
    # Email du cabinet (celui qui reçoit les rappels)
    CABINET_EMAIL = os.environ.get('CABINET_EMAIL', 'zomahoundorianne@gmail.com')
    
    # Configuration email (Gmail)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    
    # Identifiants Gmail (à mettre dans les variables d'environnement)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cedar_o.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clé secrète pour JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'cedar-o-secret-key-2026')