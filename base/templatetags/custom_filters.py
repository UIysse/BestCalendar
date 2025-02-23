from django import template
from datetime import timedelta

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
