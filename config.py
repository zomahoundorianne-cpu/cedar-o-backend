# config.py
class Config:
    # 👇 EMAIL DU CABINET (celui qui reçoit les rappels)
    CABINET_EMAIL = "zomahoundorianne@gmail.com"  # À remplacer plus tard
    
    # 👇 Configuration pour l'envoi des emails (avec Gmail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "zomahoundorianne@gmail.com" # Ton email (celui qui envoie)
    MAIL_PASSWORD = "kcsm csoj vukz kala" # À configurer plus tard
    
    # Configuration base de données
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cedar_o.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
