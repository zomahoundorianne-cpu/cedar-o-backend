# test_email_simple.py
import smtplib
from email.mime.text import MIMEText

# Mets TES vraies infos ici
EMAIL = "zomahoundorianne@gmail.com"
PASSWORD = "kcsm csoj vukz kala"
DESTINATAIRE = "zomahoundorianne@gmail.com"  # À toi pour tester

print("🔄 Test de connexion Gmail...")

try:
    # Connexion
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    print("✅ Connexion réussie !")
    
    # Création du message
    msg = MIMEText("""
    Bonjour,
    
    Ceci est un test de l'application Cedar-O.
    Si tu reçois ce message, la configuration email fonctionne !
    
    Bravo ! 🎉
    """)
    msg['Subject'] = "🔧 Test Cedar-O"
    msg['From'] = EMAIL
    msg['To'] = DESTINATAIRE
    
    # Envoi
    server.send_message(msg)
    server.quit()
    print("✅ Email envoyé ! Vérifie ta boîte de réception.")
    
except Exception as e:
    print(f"❌ Erreur : {str(e)}")