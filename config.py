import os

class Config:
    CABINET_EMAIL = os.environ.get('CABINET_EMAIL', 'zomahoundorianne@gmail.com')
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Railway fournit un volume persistant
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///cedar_o.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False