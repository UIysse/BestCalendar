from django.contrib import admin

# Register your models here.
from .models import Employe, Topic, Message, Entreprise, AdministrateurPlanning, Poste, TeamPlanning

admin.site.register(Employe)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Entreprise)
admin.site.register(AdministrateurPlanning)
admin.site.register(Poste)
admin.site.register(TeamPlanning)