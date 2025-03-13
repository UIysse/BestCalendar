from django import template
from datetime import timedelta
from base.models import Week

register = template.Library()

@register.filter
def zip_lists(a, b):
    """Permet de zipper deux listes dans les templates Django"""
    return zip(a, b)


@register.filter
def add_days(value, days): #Permet d'obtenir l'année correctement affichée pour la premiere semaine de lannée suivante (en suivant la norme 8601 à savoir le premier jeudi de l'année)
    """Ajoute un nombre de jours à une date"""
    if isinstance(value, (str,)):
        return value  # Retourne tel quel si ce n'est pas une date
    return value + timedelta(days=int(days))

@register.simple_tag
def travail_hebdo(emp, semaine, annee):
    """
    Filtre pour appeler la méthode `Temps_Travail_Hebdomadaire_Planning` d'un employé.
    Exemple d'utilisation : {{ emp|travail_hebdo:"9,2025" }}
    """
    try:
        semaine = int(semaine)
        annee = int(annee)
        return emp.Temps_Travail_Hebdomadaire_Planning(semaine, annee)
    except Exception as e:
        return f"Erreur: {str(e)}"
    
@register.simple_tag(takes_context=True)
def travail_Journalier_Entreprise(context, jour, semaine, annee):
    """
    Calcul les heures journalières pour le footer (tous les employés compris)
    """
    try:
        user = context['request'].user
        semaine = int(semaine)
        annee = int(annee)
        jour = int(jour)

        # Récupérer une instance de `Week` pour appeler la méthode
        week_instance = Week.objects.filter(week_number=semaine, year=annee).first()

        if not week_instance:
            return "Semaine introuvable"

        return week_instance.travail_Journalier_Entreprise(jour, semaine, annee, user)

    except Exception as e:
        return f"Erreur: {str(e)}"