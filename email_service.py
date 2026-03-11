# email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from models import RendezVous, Etudiant
from config import Config
import socket

# Configuration du timeout global pour les connexions réseau
socket.setdefaulttimeout(15)  # Timeout de 15 secondes maximum

def envoyer_rappel_etudiant(rdv, etudiant, type_rappel):
    """
    Envoie un email pour un étudiant spécifique
    type_rappel: 'jour_j', '2_jours', 'veille'
    """
    try:
        # Formater la date du rendez-vous
        date_rdv = rdv.date_rdv.strftime('%d/%m/%Y à %H:%M')
        
        # Déterminer le sujet selon le type de rappel
        sujets = {
            'jour_j': f"🔔 RAPPEL JOUR J - Rendez-vous avec {etudiant.prenom} {etudiant.nom} aujourd'hui",
            '2_jours': f"📅 RAPPEL J-2 - Rendez-vous avec {etudiant.prenom} {etudiant.nom} dans 2 jours",
            'veille': f"⏰ RAPPEL VEILLE - Rendez-vous avec {etudiant.prenom} {etudiant.nom} demain"
        }
        
        sujet = sujets.get(type_rappel, "Rappel de rendez-vous Cedar-O")
        
        # Messages personnalisés
        messages = {
            'jour_j': f"aujourd'hui {date_rdv}",
            '2_jours': f"dans 2 jours, le {date_rdv}",
            'veille': f"demain, le {date_rdv}"
        }
        
        message_rappel = messages.get(type_rappel, f"le {date_rdv}")
        
        # Construire l'email HTML
        corps_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
                .header {{ background-color: #0A1929; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .info {{ background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .etudiant {{ font-size: 18px; font-weight: bold; color: #0A1929; }}
                .date {{ color: #F59E0B; font-weight: bold; font-size: 16px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌲 Cedar-O</h1>
                <h2>Cabinet Conseil</h2>
            </div>
            
            <div class="content">
                <h3>Bonjour,</h3>
                
                <p><strong>Rappel : prendre des nouvelles de</strong></p>
                
                <div class="info">
                    <p class="etudiant">👤 {etudiant.prenom} {etudiant.nom}</p>
                    <p class="date">📅 {message_rappel}</p>
                    <p>📞 Téléphone: {etudiant.telephone or 'Non renseigné'}</p>
                    <p>🎓 Formation: {etudiant.formation or '-'}</p>
                    <p>🌍 Pays: {etudiant.pays_destination or '-'}</p>
                </div>
                
                {rdv.notes and f"<p><strong>Notes du rendez-vous :</strong><br>{rdv.notes}</p>"}
                
                <p style="margin-top: 20px;">Cordialement,<br>L'équipe Cedar-O</p>
            </div>
            
            <div class="footer">
                <p>🌲 Cedar-O - Accompagnement vers l'international</p>
                <p>📞 Bénin: +229 0167800170 | Togo: +228 96340909</p>
            </div>
        </body>
        </html>
        """
        
        # Version texte simple
        corps_texte = f"""
        Rappel : prendre des nouvelles de {etudiant.prenom} {etudiant.nom}
        
        {message_rappel}
        
        Téléphone: {etudiant.telephone or 'Non renseigné'}
        Formation: {etudiant.formation or '-'}
        Pays: {etudiant.pays_destination or '-'}
        {f"Notes: {rdv.notes}" if rdv.notes else ""}
        
        Cordialement,
        L'équipe Cedar-O
        """
        
        # Envoyer l'email
        envoyer_email(
            destinataire=Config.CABINET_EMAIL,
            sujet=sujet,
            corps_html=corps_html,
            corps_texte=corps_texte
        )
        
        print(f"✅ Rappel '{type_rappel}' envoyé pour {etudiant.prenom} {etudiant.nom}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi rappel: {str(e)}")
        return False

def verifier_et_envoyer_rappels():
    """
    Vérifie tous les rendez-vous et envoie les rappels nécessaires
    """
    try:
        aujourdhui = datetime.now().date()
        maintenant = datetime.now()
        
        print("="*50)
        print(f"🔍 DÉBOGAGE - Date du jour: {aujourdhui}")
        print(f"🔍 DÉBOGAGE - Heure: {maintenant.strftime('%H:%M:%S')}")
        print("="*50)
        
        # Chercher tous les rendez-vous à venir
        rendezvous = RendezVous.query.filter(
            RendezVous.statut == 'à venir'
        ).all()
        
        print(f"🔍 DÉBOGAGE - Rendez-vous à venir trouvés: {len(rendezvous)}")
        
        if len(rendezvous) == 0:
            print("📭 DÉBOGAGE - Aucun rendez-vous à venir")
            return 0
        
        rappels_envoyes = 0
        
        for i, rdv in enumerate(rendezvous):
            etudiant = Etudiant.query.get(rdv.etudiant_id)
            if not etudiant:
                print(f"⚠️ DÉBOGAGE - Étudiant non trouvé pour rdv {rdv.id}")
                continue
            
            date_rdv = rdv.date_rdv.date()
            jours_avant = (date_rdv - aujourdhui).days
            
            print(f"\n📅 DÉBOGAGE - Rendez-vous #{i+1}:")
            print(f"   - ID: {rdv.id}")
            print(f"   - Étudiant: {etudiant.prenom} {etudiant.nom}")
            print(f"   - Date RDV: {date_rdv}")
            print(f"   - Jours avant: {jours_avant}")
            print(f"   - Statut: {rdv.statut}")
            
            # Jour J (le jour même)
            if jours_avant == 0 and maintenant.hour < 10:  # Avant 10h
                print(f"   ✅ Condition JOUR J remplie (jours_avant=0, heure<10)")
                if envoyer_rappel_etudiant(rdv, etudiant, 'jour_j'):
                    rappels_envoyes += 1
                    print(f"   ✅ Rappel JOUR J envoyé")
                else:
                    print(f"   ❌ Échec envoi rappel JOUR J")
            
            # 2 jours avant
            elif jours_avant == 2:
                print(f"   ✅ Condition J-2 remplie (jours_avant=2)")
                if envoyer_rappel_etudiant(rdv, etudiant, '2_jours'):
                    rappels_envoyes += 1
                    print(f"   ✅ Rappel J-2 envoyé")
                else:
                    print(f"   ❌ Échec envoi rappel J-2")
            
            # Veille (1 jour avant)
            elif jours_avant == 1:
                print(f"   ✅ Condition VEILLE remplie (jours_avant=1)")
                if envoyer_rappel_etudiant(rdv, etudiant, 'veille'):
                    rappels_envoyes += 1
                    print(f"   ✅ Rappel VEILLE envoyé")
                else:
                    print(f"   ❌ Échec envoi rappel VEILLE")
            
            else:
                print(f"   ⏳ Condition non remplie (jours_avant={jours_avant})")
        
        print("\n" + "="*50)
        print(f"📧 DÉBOGAGE - TOTAL rappels envoyés: {rappels_envoyes}")
        print("="*50)
        return rappels_envoyes
        
    except Exception as e:
        print(f"❌ DÉBOGAGE - Erreur dans verifier_et_envoyer_rappels: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

def envoyer_email(destinataire, sujet, corps_html, corps_texte=""):
    """
    Fonction pour envoyer un email avec timeout réduit
    """
    try:
        print(f"📧 DÉBOGAGE - Tentative d'envoi email à {destinataire}")
        print(f"📧 DÉBOGAGE - Sujet: {sujet}")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = sujet
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = destinataire
        
        if corps_texte:
            part_texte = MIMEText(corps_texte, 'plain')
            msg.attach(part_texte)
        
        part_html = MIMEText(corps_html, 'html')
        msg.attach(part_html)
        
        print(f"📧 DÉBOGAGE - Connexion à {Config.MAIL_SERVER}:{Config.MAIL_PORT} (timeout 10s)")
        
        # Connexion avec timeout explicite
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT, timeout=10)
        server.starttls()
        
        print(f"📧 DÉBOGAGE - Login avec {Config.MAIL_USERNAME}")
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        
        print(f"📧 DÉBOGAGE - Envoi du message")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ DÉBOGAGE - Email envoyé avec succès")
        return True
        
    except socket.timeout:
        print(f"❌ DÉBOGAGE - Timeout: La connexion a pris trop de temps")
        return False
    except smtplib.SMTPAuthenticationError:
        print(f"❌ DÉBOGAGE - Erreur d'authentification: Vérifie ton mot de passe d'application")
        return False
    except Exception as e:
        print(f"❌ DÉBOGAGE - Erreur envoi email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Pour tester
if __name__ == '__main__':
    print("🔍 Vérification des rappels...")
    verifier_et_envoyer_rappels()