Set-ExecutionPolicy Unrestricted -Scope Process
.\env\Scripts\activate
python manage.py runserver
python manage.py populate_weeks
digitalocean :
source env/bin/activate
deactivate
pkill gunicorn
gunicorn --bind 0.0.0.0:8000 BestCalendar.wsgi:application

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