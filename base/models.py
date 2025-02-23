from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
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
        ('#FF0000', 'Rouge'), 
        ('#808080', 'Gris'),  # Couleur gris ajoutée
    ]

    couleur = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        default='#FF0000'  # Default color set to red
    )


    def __str__(self) -> str:
        return self.name

class Entreprise(models.Model):
    name = models.CharField(max_length=255)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)
    badgeuse_account = models.OneToOneField(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enterprise',
        help_text="The badgeuse account associated with this enterprise.",
    )

    def clean(self):
        if self.badgeuse_account and self.badgeuse_account.user_type != 'badgeuse':
            raise ValidationError("badgeuse_account must be a user of type 'badgeuse'.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
    
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('manager', 'Manager'),
        ('badgeuse', 'Badgeuse'),
    )

    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='manager',
        help_text="Indicates whether the user is a manager or a badgeuse."
    )

    entreprise = models.ForeignKey(
        'Entreprise',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='managers',
        help_text="The entreprise this user manages (if applicable)."
    )

    managed_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_badgeuses',
        help_text="If this user is a badgeuse, this links to the manager that created them."
    )

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def is_manager(self):
        return self.user_type == 'manager'

    def is_badgeuse(self):
        return self.user_type == 'badgeuse'

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

class UsersBadgedShifts(models.Model):
    Employe = models.ForeignKey(Employe, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    heures_arrivees = models.JSONField(default=list, blank=True)  # Liste d'heures
    heures_departs = models.JSONField(default=list, blank=True)  # Liste d'heures
    #TempsTravailEffectif = models.DurationField(default=timedelta())  # Durée de travail effective
    @property
    def calcul_temps_travail(self):
        total = timedelta()
        arrivees = self.heures_arrivees
        departs = self.heures_departs

        longueur = max(len(arrivees), len(departs))

        for i in range(longueur):
            arrivee = datetime.strptime(arrivees[i], '%H:%M:%S').time() if i < len(arrivees) else None
            depart = datetime.strptime(departs[i], '%H:%M:%S').time() if i < len(departs) else None

            if arrivee and depart:
                total += datetime.combine(self.date, depart) - datetime.combine(self.date, arrivee)
            elif arrivee and not depart:
                # Si le départ est manquant, on fixe 18:00 et mettre un sigle d'alerte sur le badge
                depart_defaut = datetime.strptime('18:00:00', '%H:%M:%S').time()
                total += datetime.combine(self.date, depart_defaut) - datetime.combine(self.date, arrivee)
            elif depart and not arrivee:
                # Si l'arrivée est manquante, on fixe 09:00 mais mettre sigle alerte sur le badge
                arrivee_defaut = datetime.strptime('09:00:00', '%H:%M:%S').time()
                total += datetime.combine(self.date, depart) - datetime.combine(self.date, arrivee_defaut)
            else:
                print(f"Avertissement : Aucun badge pour l'entrée {i+1}")

        return total

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
        ('Arrêt de travail', 'Arrêt de travail'),
        ('Absence injustifiée', 'Absence injustifiée'),
        ('Autre..', 'Autre..'),
    ]

    TypeAbsence = models.CharField(
        max_length=25,
        choices=ABSENCE_CHOICES,
        default='Congé sans solde'  # Default 
    )

    # New boolean field for overtime
    is_overtime = models.BooleanField(default=False, verbose_name="Shift en heures supplémentaires")

        # New boolean field for leave
    is_absence = models.BooleanField(default=False, verbose_name="Absence")
    # 🔥 Ajout d'une relation avec UsersBadgedShifts
    users_badged_shift = models.ForeignKey(
        'UsersBadgedShifts', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="team_planning"
    )
    def LoadMydict():
        pass

    def AddEmploye(self,  empId, day):
        self.mydict[day] = empId
        self.save()

    def __str__(self):
        return self.date.strftime("%Y-%m-%d") + ' ' + self.Employe.firstname + ' ' + self.Employe.name + ' ' + str(self.id)

class Week(models.Model):
    week_number = models.IntegerField()
    first_day = models.DateField(max_length=20)
    year = models.IntegerField()  # 🆕 Ajout de l'année

    def __str__(self):
        return f"Semaine {self.week_number} - {self.year} ({self.first_day})"

    class Meta:
        ordering = ['year', 'week_number']
        unique_together = ('week_number', 'year')  # Assure que chaque (semaine, année) est unique

    def save(self, *args, **kwargs):
        """Auto-calcule l'année avant de sauvegarder."""
        if not self.year:  # Only set year if not already provided
            self.year = self.first_day.year  # 🆕 Extrait automatiquement l'année depuis le premier jour de la semaine
        super().save(*args, **kwargs)

    def get_week_days(self):
        """Retourne une liste de tous les jours dans cette semaine."""
        return [self.first_day + timedelta(days=i) for i in range(7)]