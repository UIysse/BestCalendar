from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta
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
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ["display_order"]  # ✅ Ensure rows are displayed in order

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
    
    def Temps_Travail_Hebdomadaire_Planning(self, semaine_chiffre, annee_chiffre):
        """
        Calcule le total des heures travaillées pour une semaine donnée.
        :param semaine: Instance de la classe Week
        :return: Durée totale sous format HH:MM:SS
        """
        # Trouver le premier jour de la semaine
        semaine_dinteret = Week.objects.filter(week_number = semaine_chiffre, year = annee_chiffre).first()
        if not semaine_dinteret:
            return "n'a pas trouvé de semaine"
        semaine_start_date = semaine_dinteret.first_day  # Supposons que `first_day` contient la date du lundi
        # Filtrer les plannings de l'employé pour la semaine donnée
        shifts = TeamPlanning.objects.none()
        for i in range (7):
            jour_date = semaine_start_date + timedelta(days=i) 
            # Ajouter les shifts du jour en excluant les absences
            shifts = shifts | TeamPlanning.objects.filter(Employe=self, date=jour_date).exclude(is_absence=True)

        total_duree = timedelta()

        for shift in shifts:
            if shift:  
                try:
                    duree = shift.duree_travail_theorique
                    if isinstance(duree, str):  
                        h, m, s = map(int, duree.split(":"))  # Convertir en timedelta
                        duree = timedelta(hours=h, minutes=m, seconds=s)
                    total_duree += duree
                except ValueError:
                    continue  # Ignorer les erreurs de conversion

        # Convertir en format HH:MM:SS
        heures, remainder = divmod(total_duree.total_seconds(), 3600)
        minutes, secondes = divmod(remainder, 60)

        return f"{int(heures):02}h{int(minutes):02}"

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

        return str(total)

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

    # New boolean field for leave
    is_unscheduled = models.BooleanField(default=False, verbose_name="Shift non prévu")

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
    
    @property
    def duree_pause_minutes(self):
        """Retourne la durée de la pause en minutes"""
        if self.duréepause:
            # Convertir en datetime pour soustraction
            pause_datetime = datetime.combine(self.date, self.duréepause)
            min_time = datetime.combine(self.date, time(0, 0))  # 00:00
            pause_duration = pause_datetime - min_time
            return int(pause_duration.total_seconds() // 60)  # Convertir en minutes
        return 0  # Retourne 0 si la pause n'est pas définie
    
    @property
    def duree_travail_theorique(self):
        """Retourne la durée de travail théorique au format HH:MM:SS"""
        if self.Heurededébut and self.heuredefin and self.duréepause:
            # Convertir les TimeField en datetime pour pouvoir les soustraire
            debut_datetime = datetime.combine(self.date, self.Heurededébut)
            fin_datetime = datetime.combine(self.date, self.heuredefin)
            pause_datetime = datetime.combine(self.date, self.duréepause)
            min_time = datetime.combine(self.date, time(0, 0))  # 00:00 pour référence
            
            # Calculer la durée totale de travail sans la pause
            duree_travail = fin_datetime - debut_datetime
            duree_pause = pause_datetime - min_time
            duree_totale = duree_travail - duree_pause

            # Retourner en format HH:MM:SS
            return str(duree_totale)
        
        return "00:00:00"  # Retourne 00:00:00 si les données sont incomplètes
    
    @property
    def duree_travail_theorique_reformulee(self):
        """Retourne la durée de travail théorique au format HH:MM:SS"""
        if self.Heurededébut and self.heuredefin and self.duréepause:
            # Convertir les TimeField en datetime pour pouvoir les soustraire
            debut_datetime = datetime.combine(self.date, self.Heurededébut)
            fin_datetime = datetime.combine(self.date, self.heuredefin)
            pause_datetime = datetime.combine(self.date, self.duréepause)
            min_time = datetime.combine(self.date, time(0, 0))  # 00:00 pour référence
            
            # Calculer la durée totale de travail sans la pause
            duree_travail = fin_datetime - debut_datetime
            duree_pause = pause_datetime - min_time
            duree_totale = duree_travail - duree_pause

            totalseconds = abs(int(duree_totale.total_seconds()))
            hours, remainder = divmod(totalseconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            # Retourner en format HH:MM:SS
            return f"{hours:02}h{minutes:02}" if totalseconds else "00:00:00"
        
        return "00:00:00"  # Retourne 00:00:00 si les données sont incomplètes
    
    @property
    def difference_travail_reel_theorique(self):
        if not self.users_badged_shift:
            return "00:00:00"
        
        """
        Retourne la différence entre la durée de travail théorique et le temps de travail effectif.
        Format : HH:MM:SS (positif si surplus, négatif si manque).
        """
        # Obtenir la durée théorique
        try:
            duree_theorique = datetime.strptime(self.duree_travail_theorique, "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
        except ValueError:
            return "00:00:00"  # Gérer les erreurs de conversion

        # Obtenir le temps de travail effectif (assumant que `calcul_temps_travail` est déjà au format HH:MM:SS)
        try:
            duree_reelle = datetime.strptime(self.users_badged_shift.calcul_temps_travail, "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
        except ValueError:
            return "00:00:00"

        # Calculer la différence (peut être négative ou positive)
        difference = int(duree_reelle.total_seconds()) - int(duree_theorique.total_seconds())
        sign = "-" if difference < 0 else ""
        total_seconds = abs(difference) # on obtient l'absolu
        # Convertir en HH:MM:SS
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        # Retourner en format HH:MM:SS
        return f"{sign}{hours:02}h{minutes:02}" if difference else "00:00:00"
    
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
    
    def travail_Journalier_Entreprise(self, jour_chiffre, semaine_chiffre, annee_chiffre, user):
        """
        Calcule le total des heures travaillées pour un jour donné (tous employés).
        """
        if jour_chiffre == 0:  #car en iso le le dimanche est le chiffre 0 - cela casse la fonction
            jour_chiffre = 7
         # Trouver le premier jour de la semaine
        semaine_dinteret = Week.objects.filter(week_number = semaine_chiffre, year = annee_chiffre).first()
        if not semaine_dinteret:
            return "n'a pas trouvé de semaine"
        semaine_start_date = semaine_dinteret.first_day  # Supposons que `first_day` contient la date du lundi
        jour_date = semaine_start_date + timedelta(days=jour_chiffre - 1)
        # Filtrer les plannings de l'employé pour la semaine donnée
        shifts = TeamPlanning.objects.filter(
            date=jour_date,
            Employe__EntrepriseRattachée=user.entreprise,  # ✅ Only employees in the same enterprise as the user
        ).exclude(is_absence=True)  # 📌 Exclure directement les absences

        total_duree = timedelta()

        for shift in shifts:
            if shift:  
                try:
                    duree = shift.duree_travail_theorique
                    if isinstance(duree, str):  
                        h, m, s = map(int, duree.split(":"))  # Convertir en timedelta
                        duree = timedelta(hours=h, minutes=m, seconds=s)
                    total_duree += duree
                except ValueError:
                    continue  # Ignorer les erreurs de conversion

        # Convertir en format HH:MM:SS
        heures, remainder = divmod(total_duree.total_seconds(), 3600)
        minutes, secondes = divmod(remainder, 60)

        return f"{int(heures):02}h{int(minutes):02}"