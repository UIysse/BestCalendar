Set-ExecutionPolicy Unrestricted -Scope Process
.\env\Scripts\activate
python manage.py runserver
python manage.py populate_weeks
digitalocean :
source env/bin/activate
deactivate
pkill gunicorn
gunicorn --bind 0.0.0.0:8000 BestCalendar.wsgi:application