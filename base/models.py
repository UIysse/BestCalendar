from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
# Create your models here.
class Poste(models.Model):
    name = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)
    COLOR_CHOICES = [
        ('#FFFFFF', 'Blanc'),
        ('#ee96fa', 'Rose'),
        ('#96bcfa', 'Bleu'),
        ('#b7fa96', 'Vert'),
        ('#faf296', 'Jaune'),
    ]

    couleur = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        default='#FF0000'  # Default color set to red
    )


    def __str__(self) -> str:
        return self.name

class Entreprise(models.Model):
    name = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)

    def __str__(self) -> str:
        return self.name

class AdministrateurPlanning(models.Model):
    name = models.CharField(max_length=100)
    entreprise = models.ForeignKey(Entreprise, on_delete = models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)

    def __str__(self) -> str:
        return self.name

class Employe(models.Model):
    Poste = models.ForeignKey(Poste, on_delete=models.SET_NULL, null=True)
    EntrepriseRattachée = models.ForeignKey(Entreprise, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, default="Nom")
    firstname = models.CharField(max_length=200, default="Prénom")
    e_mail = models.CharField(max_length=200, default="default@example.com")
    phone_number = models.CharField(max_length=12, default="0634567890")
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + ' ' + self.firstname

class TeamPlanning(models.Model):
    mydict={}
    Employe = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    Heurededébut = models.TimeField(auto_now=False, auto_now_add=False)
    heuredefin = models.TimeField(auto_now=False, auto_now_add=False)
    duréepause = models.TimeField(auto_now=False, auto_now_add=False)   #models.DurationField(auto_now=False, auto_now_add=False)
    Poste = models.ForeignKey(Poste, on_delete=models.SET_NULL, null=True)
    note = models.CharField(max_length=200)
    ABSENCE_CHOICES = [
        ('', "Sélectionnez un type d'absence"),  # Default empty option
        ('Congé sans solde', 'Congé sans solde'),
        ('Congé payé', 'Congé payé'),
    ]

    TypeAbsence = models.CharField(
        max_length=25,
        choices=ABSENCE_CHOICES,
        default='Congé sans solde'  # Default 
    )
    def LoadMydict():
        pass

    def AddEmploye(self,  empId, day):
        self.mydict[day] = empId
        self.save()

    def __str__(self):
        return self.date.strftime("%Y-%m-%d") + ' ' + self.Employe.firstname + ' ' + self.Employe.name + ' ' + str(self.id)

class Message(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    employe = models.ForeignKey(Employe, on_delete = models.CASCADE)
    body = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]