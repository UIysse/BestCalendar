from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AbstractUser
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
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
    
class CustomUser(AbstractUser):
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True)

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
    employee_CodePin = models.CharField(max_length=4, unique=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.employee_CodePin:
            # Ensure uniqueness of the employee_number
            while True:
                unique_number = get_random_string(length=4, allowed_chars='0123456789')
                if not Employe.objects.filter(employee_CodePin=unique_number).exists():
                    self.employee_CodePin = unique_number
                    break
        super().save(*args, **kwargs)

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
