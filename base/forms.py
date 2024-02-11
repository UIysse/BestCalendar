# forms.py
from django import forms
from django.core.validators import EmailValidator
from .models import Employe, TeamPlanning, Entreprise

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['name', 'firstname', 'Poste','phone_number', 'e_mail', 'EntrepriseRattachée']  # Add other fields as needed
        labels = {'name' : 'Nom',
                   'firstname' : 'Prénom',
                     'Poste' : 'Poste',
                     'phone_number' : 'Téléphone',
                       'e_mail' : 'E-mail',
                         'EntrepriseRattachée' : 'Entreprise employeur'}
        

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EmployeForm, self).__init__(*args, **kwargs)
        if user is not None and not user.is_anonymous:
            self.fields['EntrepriseRattachée'].queryset = Entreprise.objects.filter(id=user.entreprise.id)


class ModifyEmployeform(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['name', 'firstname', 'Poste','phone_number', 'e_mail', 'EntrepriseRattachée']

class ModifyPlanningForm(forms.ModelForm):
    #employe fill par cellule
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label='Date')#initial fill par cellule
    Heurededébut = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), label='Début', initial="09:00")
    heuredefin = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), label='Fin', initial="18:00")
    duréepause = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), label='Pause', initial="01:00")
    shift_Id = forms.IntegerField(widget=forms.HiddenInput(), required=False,)
    #Ne pas oublier de convertir la duréepause en durationfield (timedelta) via une diff avec 00:00
    note = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'placeholder': 'Ajouter une note'}),
        required=False,  # Use this if the field is not mandatory,
        label = "Note"
    )
    TypeAbsence = forms.ChoiceField(
        choices=TeamPlanning.ABSENCE_CHOICES,  # Use the choices from your model
        required=False,
        label="", #left empty for better design but originally was "type d'absence"
        widget=forms.Select(attrs={'class': 'form-select'})  # Using Bootstrap class as an example
    )
    # Modifier the type of the form below
    ACTION_CHOICES = [
        ('DeleteShift', 'DeleteShift'),
        ('EditShift', 'EditShift'),
        ('AddShift', 'AddShift'),
        ('NouvelleAbsence', 'NouvelleAbsence'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.HiddenInput(), required=False)

    class Meta:
        model = TeamPlanning
        fields = ['Employe', 'Poste']
        labels = {'Employe' : 'Employe',
                  'Poste' : "Poste"}
        
class ContactForm(forms.Form):
    name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Nom'}),
        required=True, label = "Nom")
    email = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'nom@exemple.com'}),
        required=True, label = "E-mail", validators=[EmailValidator()])
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': '0100000000'}),
        required=False, label = "Téléphone")
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Sujet'}),
        required=True, label = "Sujet")
    message = forms.CharField(widget=forms.Textarea, required=True, label = "Message")