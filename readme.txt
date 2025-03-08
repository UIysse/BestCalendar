1) activer user glenn sudo su - glenn
2) activer l'environnement env
source /home/glenn/BestCalendar/env/bin/activate
normalement cest activé.
3) se positionner dans le bon dossier
cd /home/glenn/BestCalendar # se met dans le dossierBestcalendar
4) sauvegarde la database
soit cp db.sqlite3 db_backup_$(date +"%Y%m%d%H%M%S").sqlite3 pour dupliquer la db
soit mv db.sqlite3 db.sqlite3.backup  # Sauvegarde en cas de problème
git stash push db.sqlite3 : Cache la base de données avant la mise à jour.
git pull origin main : Récupère les changements depuis GitHub.
git stash pop : Remet SQLite en place après la mise à jour.
ramener la db :
mv db.sqlite3.backup db.sqlite3
5)
si un probleme chatgpt explique comment connaitre les backup de la database et les reimplémenter.
si un mdp pour glenn est demandé : 111990
6) le mail application : pharmashiftcontact@gmail.com pw : Pcsd93200*
Set-ExecutionPolicy Unrestricted -Scope Process
.\env\Scripts\activate
python manage.py runserver
python manage.py populate_weeks
digitalocean :
source env/bin/activate
deactivate
pkill gunicorn
gunicorn --bind 0.0.0.0:8000 BestCalendar.wsgi:application
je suis passé en https avec :
sudo certbot --nginx -d pharmashift.fr -d www.pharmashift.fr
a tester : 
sudo nano /etc/nginx/sites-available/BestCalendar
server {
    listen 80;
    server_name pharmashift.fr www.pharmashift.fr;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/glenn/BestCalendar;  # Update with the actual path to your static files
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}


console pour tester gunicorn :
gunicorn --bind 0.0.0.0:8000 BestCalendar.wsgi
visiter le site http://161.35.85.238:8000

The error you're seeing:

css
Copier le code
[ERROR] connection to /run/gunicorn.sock failed
This indicates that Gunicorn is attempting to bind to a Unix socket (/run/gunicorn.sock), but something is preventing the connection.

Here’s how to fix this issue step by step.

🔧 Root Cause:
The Unix socket either doesn’t exist or has incorrect permissions.
Nginx cannot communicate with Gunicorn through the socket.
🛠️ Solution 1: Ensure Gunicorn Creates the Socket
Check if the Socket Exists:
bash
Copier le code
ls -l /run/gunicorn.sock
If the socket does not exist: This confirms Gunicorn isn’t creating it. Proceed to the next step.
If the socket exists but still fails: The issue is likely permissions. Skip to Solution 2.
Modify Gunicorn Service to Bind Properly
Edit the Gunicorn service file:
bash
Copier le code
sudo nano /etc/systemd/system/gunicorn.service
Replace this line (if it exists):

ini
Copier le code
ExecStart=/home/glenn/BestCalendar/env/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock BestCalendar.wsgi:application
With this:

ini
Copier le code
ExecStart=/home/glenn/BestCalendar/env/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 BestCalendar.wsgi:application
Reload systemd and Restart Gunicorn:
bash
Copier le code
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
Check Gunicorn Status:
bash
Copier le code
sudo systemctl status gunicorn
The error should disappear.
Update Nginx to Proxy to Port 8000 Instead of the Socket:
Edit your Nginx config:
bash
Copier le code
sudo nano /etc/nginx/sites-available/BestCalendar
Locate:

nginx
Copier le code
proxy_pass http://unix:/run/gunicorn.sock;
Replace it with:

nginx
Copier le code
proxy_pass http://127.0.0.1:8000;
Restart Nginx:
bash
Copier le code
sudo nginx -t
sudo systemctl restart nginx


MISE A JOUR DES WEEK PREEXISTANTE POUR QU ELLES AIENT LE CHAMPS ANNEE
Maintenant que nous avons ajouté l'année, il faut mettre à jour les enregistrements existants.

Exécute ce script Python dans Django Shell :

bash
Copier
Modifier
python manage.py shell
Puis, tape ce script :

python
Copier
Modifier
from base.models import Week  # Importe ton modèle

# Met à jour toutes les semaines existantes
for week in Week.objects.all():
    week.year = week.first_day.year  # Assigne l'année depuis first_day
    week.save()

print("Mise à jour terminée !")



----------------------AJOUT DES SEMAINES POUR LES ANNEES 2025 ET 2025 attention il faut respecter la norme 8601 (la premiere semaine de l'année X est la premeire semaine qui contient un jeudi)
Exécute ce script dans Django Shell (python manage.py shell):
from datetime import date, timedelta
from base.models import Week

def generate_weeks_for_year(year):
    """
    Génère toutes les semaines pour une année donnée en respectant la norme ISO 8601.
    """

    # Trouver le premier jour de la première semaine ISO de l'année
    first_day = date.fromisocalendar(year, 1, 1)  # Lundi de la semaine 1

    for week_number in range(1, 54):  # Maximum 53 semaines possibles
        week_start = first_day + timedelta(weeks=week_number - 1)

        # Vérifier si la semaine appartient bien à l'année demandée
        if week_start.year < year:
            continue  # Évite d'ajouter une semaine qui appartient à l'année précédente

        if week_number == 53:
            # Vérifier si la semaine déborde sur l'année suivante
            jours_suivants = sum(1 for i in range(7) if (week_start + timedelta(days=i)).year == year + 1)

            if jours_suivants >= 4:
                print(f"⚠️ Semaine {week_number} appartient majoritairement à {year + 1}, non créée pour {year}.")
                continue  # Ne pas créer la semaine 53 si elle appartient majoritairement à l'année suivante

        # Création de la semaine
        week, created = Week.objects.get_or_create(
            week_number=week_number,
            year=year,
            defaults={'first_day': week_start}
        )

        if created:
            print(f"✅ Semaine {week_number} créée : {week_start}")
        else:
            print(f"⚠️ Semaine {week_number} existante, non modifiée.")

# Générer les semaines pour 2025 et 2026
generate_weeks_for_year(2025)
generate_weeks_for_year(2026)

en python shell :
from base.views import generate_weeks_for_year
generate_weeks_for_year(2026)

---------------SUPPRIMER LES SEMAINES ANNEE X 
from base.models import Week

# Supprimer les semaines de 2025 uniquement
Week.objects.filter(year=2025).delete()

print("Les semaines de 2025 ont été supprimées.")

----------------IMPRIMER LES SEMAINE ANNEE X
from base.models import Week

# Vérifier combien de semaines existent pour 2025
weeks_2025 = Week.objects.filter(year=2025)

# Afficher les semaines trouvées
if weeks_2025.exists():
    print(f"✅ {weeks_2025.count()} semaines trouvées pour 2025.")
    for week in weeks_2025:
        print(f"Semaine {week.week_number} - {week.first_day}")
else:
    print("❌ Aucune semaine trouvée pour 2025.")

