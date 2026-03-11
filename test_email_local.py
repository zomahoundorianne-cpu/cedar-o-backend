# test_email_local.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Mets TES vraies infos en dur pour le test
MAIL_USERNAME = "zomahoundorianne@gmail.com"
MAIL_PASSWORD = "kcsm csoj vukz kala"  # Ton mot de passe d'application
CABINET_EMAIL = "zomahoundorianne@gmail.com"

print("="*50)
print("🔧 TEST EMAIL LOCAL")
print("="*50)

print(f"📧 Configuration:")
print(f"   - MAIL_USERNAME: {MAIL_USERNAME}")
print(f"   - MAIL_SERVER: smtp.gmail.com")
print(f"   - MAIL_PORT: 587")
print(f"   - Destinataire: {CABINET_EMAIL}")

try:
    # Créer le message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "🔧 Test local Cedar-O"
    msg['From'] = MAIL_USERNAME
    msg['To'] = CABINET_EMAIL
    
    corps = """
    <html>
    <body>
        <h2>Test local d'envoi d'email</h2>
        <p>Si tu reçois ce message, la configuration email fonctionne en local !</p>
        <p>✅ Félicitations !</p>
    </body>
    </html>
    """
    
    part_html = MIMEText(corps, 'html')
    msg.attach(part_html)
    
    print(f"\n📧 Connexion à smtp.gmail.com:587...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    server.starttls()
    
    print(f"📧 Login avec {MAIL_USERNAME}...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    
    print(f"📧 Envoi du message...")
    server.send_message(msg)
    server.quit()
    
    print("✅ EMAIL ENVOYÉ AVEC SUCCÈS !")
    print("📬 Vérifie ta boîte de réception !")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ ERREUR D'AUTHENTIFICATION:")
    print(f"   {str(e)}")
    print("\n🔑 Solution:")
    print("   1. Va sur: https://myaccount.google.com/apppasswords")
    print("   2. Génére un NOUVEAU mot de passe d'application")
    print("   3. Copie-le SANS espaces")
    print("   4. Remplace MAIL_PASSWORD dans ce script")
    
except socket.timeout:
    print(f"❌ TIMEOUT: La connexion a pris trop de temps")
    
except Exception as e:
    print(f"❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()