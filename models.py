# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Etudiant(db.Model):
    __tablename__ = 'etudiants'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    pays_destination = db.Column(db.String(100))
    ecole = db.Column(db.String(200))
    formation = db.Column(db.String(200))
    photo = db.Column(db.String(500))  # URL ou chemin de la photo
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation avec les rendez-vous
    rendezvous = db.relationship('RendezVous', backref='etudiant', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone,
            'pays_destination': self.pays_destination,
            'ecole': self.ecole,
            'formation': self.formation,
            'photo': self.photo,
            'date_inscription': self.date_inscription.isoformat() if self.date_inscription else None
        }

class RendezVous(db.Model):
    __tablename__ = 'rendezvous'
    
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey('etudiants.id'), nullable=False)
    date_rdv = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    statut = db.Column(db.String(20), default='à venir')  # à venir, effectué, annulé
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'etudiant_id': self.etudiant_id,
            'date_rdv': self.date_rdv.isoformat() if self.date_rdv else None,
            'notes': self.notes,
            'statut': self.statut,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None
        }
    
# Ajouter dans models.py (à côté des classes Etudiant et RendezVous)

class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' ou 'user'
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'role': self.role,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None
        }