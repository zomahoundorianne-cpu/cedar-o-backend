from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from models import db, Etudiant, RendezVous, Utilisateur
from email_service import verifier_et_envoyer_rappels
from config import Config
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image
import re

app = Flask(__name__)

# Configuration JWT - version ultra simple
app.config['JWT_SECRET_KEY'] = 'cedar-o'  # Clé très simple
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

# ===== GESTIONNAIRES D'ERREURS JWT AJOUTÉS =====
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "success": False,
        "error": "Token invalide",
        "msg": str(error)
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "success": False,
        "error": "Token manquant",
        "msg": "Authorization header manquant ou mal formaté"
    }), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "success": False,
        "error": "Token expiré",
        "msg": "Veuillez vous reconnecter"
    }), 401
# ===== FIN GESTIONNAIRES JWT =====

# Configuration pour les uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuration base de données
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

# Initialisation base de données
db.init_app(app)

# Créer les tables
with app.app_context():
    db.create_all()
    print("✅ Base de données créée!")

@app.route('/', methods=['GET'])
def accueil():
    return jsonify({
        "message": "API Cedar-O",
        "status": "OK"
    })

# -------------------- ROUTES ÉTUDIANTS --------------------
@app.route('/api/etudiants', methods=['GET'])
@jwt_required()
def get_etudiants():
    etudiants = Etudiant.query.all()
    return jsonify({
        "success": True,
        "data": [e.to_dict() for e in etudiants]
    })

@app.route('/api/etudiants', methods=['POST'])
@jwt_required()
def add_etudiant():
    data = request.json
    nouvel_etudiant = Etudiant(
        nom=data['nom'],
        prenom=data['prenom'],
        email=data['email'],
        telephone=data.get('telephone'),
        pays_destination=data.get('pays_destination'),
        ecole=data.get('ecole'),
        formation=data.get('formation'),
        photo=data.get('photo')
    )
    db.session.add(nouvel_etudiant)
    db.session.commit()
    return jsonify({"success": True, "data": nouvel_etudiant.to_dict()}), 201

@app.route('/api/etudiants/<int:id>', methods=['PUT'])
@jwt_required()
def update_etudiant(id):
    try:
        etudiant = Etudiant.query.get(id)
        if not etudiant:
            return jsonify({"success": False, "error": "Étudiant non trouvé"}), 404
        
        data = request.json
        if 'nom' in data: etudiant.nom = data['nom']
        if 'prenom' in data: etudiant.prenom = data['prenom']
        if 'email' in data: 
            existing = Etudiant.query.filter(Etudiant.email == data['email'], Etudiant.id != id).first()
            if existing:
                return jsonify({"success": False, "error": "Email déjà utilisé"}), 400
            etudiant.email = data['email']
        if 'telephone' in data: etudiant.telephone = data['telephone']
        if 'pays_destination' in data: etudiant.pays_destination = data['pays_destination']
        if 'ecole' in data: etudiant.ecole = data['ecole']
        if 'formation' in data: etudiant.formation = data['formation']
        if 'photo' in data: etudiant.photo = data['photo']
        
        db.session.commit()
        return jsonify({"success": True, "data": etudiant.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/etudiants/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_etudiant(id):
    try:
        etudiant = Etudiant.query.get(id)
        if not etudiant:
            return jsonify({"success": False, "error": "Étudiant non trouvé"}), 404
        db.session.delete(etudiant)
        db.session.commit()
        return jsonify({"success": True, "message": "Étudiant supprimé"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------- ROUTES RENDEZ-VOUS --------------------
@app.route('/api/etudiants/<int:etudiant_id>/rendezvous', methods=['GET'])
@jwt_required()
def get_rendezvous(etudiant_id):
    etudiant = Etudiant.query.get(etudiant_id)
    if not etudiant:
        return jsonify({"success": False, "error": "Étudiant non trouvé"}), 404
    rendezvous = RendezVous.query.filter_by(etudiant_id=etudiant_id).all()
    return jsonify({"success": True, "data": [rdv.to_dict() for rdv in rendezvous]})

@app.route('/api/etudiants/<int:etudiant_id>/rendezvous', methods=['POST'])
@jwt_required()
def add_rendezvous(etudiant_id):
    data = request.json
    nouveau_rdv = RendezVous(
        etudiant_id=etudiant_id,
        date_rdv=datetime.fromisoformat(data['date_rdv']),
        notes=data.get('notes')
    )
    db.session.add(nouveau_rdv)
    db.session.commit()
    return jsonify({"success": True, "data": nouveau_rdv.to_dict()}), 201

@app.route('/api/rendezvous/<int:id>', methods=['PUT'])
@jwt_required()
def update_rendezvous(id):
    rdv = RendezVous.query.get(id)
    if not rdv:
        return jsonify({"success": False, "error": "Rendez-vous non trouvé"}), 404
    
    data = request.json
    if 'date_rdv' in data: rdv.date_rdv = datetime.fromisoformat(data['date_rdv'])
    if 'notes' in data: rdv.notes = data['notes']
    if 'statut' in data: rdv.statut = data['statut']
    
    db.session.commit()
    return jsonify({"success": True, "data": rdv.to_dict()})

@app.route('/api/rendezvous/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_rendezvous(id):
    rdv = RendezVous.query.get(id)
    if not rdv:
        return jsonify({"success": False, "error": "Rendez-vous non trouvé"}), 404
    db.session.delete(rdv)
    db.session.commit()
    return jsonify({"success": True, "message": "Rendez-vous supprimé"})

# -------------------- ROUTES PHOTOS --------------------
@app.route('/api/upload-photo', methods=['POST'])
@jwt_required()
def upload_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({"success": False, "error": "Aucun fichier envoyé"}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({"success": False, "error": "Nom de fichier vide"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = filename.replace(' ', '_')
            import time
            filename = f"{int(time.time())}_{filename}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                img = Image.open(filepath)
                if max(img.size) > 800:
                    img.thumbnail((800, 800))
                    img.save(filepath)
            except:
                pass
            
            photo_url = f"/uploads/{filename}"
            return jsonify({"success": True, "photo_url": photo_url}), 201
        else:
            return jsonify({"success": False, "error": "Type de fichier non autorisé"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -------------------- ROUTES AUTH --------------------
@app.route('/api/init-admin', methods=['GET'])
def init_admin():
    try:
        admin = Utilisateur.query.filter_by(email='admin@cedar-o.com').first()
        if admin:
            return jsonify({"message": "Admin déjà existant"}), 200
        
        mot_de_passe_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = Utilisateur(
            nom='Administrateur',
            email='admin@cedar-o.com',
            mot_de_passe=mot_de_passe_hash,
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        return jsonify({"success": True, "message": "Admin créé"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        utilisateur = Utilisateur.query.filter_by(email=data.get('email')).first()
        
        if not utilisateur or not bcrypt.check_password_hash(utilisateur.mot_de_passe, data.get('mot_de_passe')):
            return jsonify({"error": "Email ou mot de passe incorrect"}), 401
        
        access_token = create_access_token(
            identity=str(utilisateur.id),
            additional_claims={
                "email": utilisateur.email,
                "nom": utilisateur.nom,
                "role": utilisateur.role
            }
        )
        return jsonify({"success": True, "token": access_token, "user": utilisateur.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- ROUTES RAPPELS --------------------
@app.route('/api/verifier-rappels', methods=['GET'])
@jwt_required()
def verifier_rappels():
    try:
        nb_rappels = verifier_et_envoyer_rappels()
        return jsonify({"success": True, "message": f"{nb_rappels} rappels envoyés"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------- DÉMARRAGE --------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)