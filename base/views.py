from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now
from .models import Employe, TeamPlanning, Week, UsersBadgedShifts, Poste
from .forms import EmployeForm, ModifyEmployeForm, ModifyPlanningForm, ContactForm, SelectionForm

# Create your views here.
from django.http import HttpResponse

employelist = [
    {'id':1, 'name': 'Lets learn python ! 1'},
    {'id':2, 'name': 'Lets learn python ! 2'},
    {'id':3, 'name': 'Lets learn python ! 3'},
]
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            pass
            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'base/contact.html', {'form': form})

def badgeuse(request):
    return render(request, 'base/badgeuse.html')
#le code qui suit gère les infos pour les tooltip sur la page planning (envoyé au client par ce code et AJAX)
# def get_badge_hours(request, employe_id, date):
#     print(f"Requête API reçue : employe_id={employe_id}, date={date}")  # Debug
#     try:
#         shift = UsersBadgedShifts.objects.get(Employe_id=employe_id, date=date)
#         data = {
#             'status': 'success',
#             'heures_arrivees': shift.heures_arrivees,
#             'heures_departs': shift.heures_departs
#         }
#         print("Données envoyées :", data)  # Debug
#         return JsonResponse(data)
#     except UsersBadgedShifts.DoesNotExist:
#         return JsonResponse({'status': 'error', 'message': 'Aucun badge trouvé'}, status=404)
    
#Le code qui suit gère le badging des employés
@csrf_exempt  # Ajoute la protection CSRF plus tard pour plus de sécurité
def badge_log(request):
    if request.method == 'POST':
        if request.user.user_type != 'badgeuse':
            return JsonResponse({'status': 'error', 'message': 'Seules les badgeuses peuvent envoyer un badge'})

        pin = request.POST.get('pin')
        entreprise_user = request.user.entreprise
        current_time = timezone.localtime().time()
        current_date = now().date()
        arrivee_ou_depart = ""
        try:
            employe = Employe.objects.get(employee_CodePin=pin, EntrepriseRattachée=entreprise_user)

            # Vérifier si un UsersBadgedShifts existe déjà pour l'employé et la date du jour
            shift, created = UsersBadgedShifts.objects.get_or_create(
                Employe=employe,
                date=current_date,
                defaults={'heures_arrivees': [], 'heures_departs': []}
            )

            if created:
                # Si le shift vient d'être créé, c'est probablement une arrivée
                shift.heures_arrivees.append(current_time.strftime('%H:%M:%S'))
                arrivee_ou_depart = "Arrivée enregistrée : " + current_time.strftime('%H:%M:%S')
            else:
                # Si le shift existe déjà, on détermine si c'est une arrivée ou un départ
                if len(shift.heures_arrivees) > len(shift.heures_departs):
                    # Si on a plus d'arrivées que de départs, c'est un départ
                    shift.heures_departs.append(current_time.strftime('%H:%M:%S'))
                    arrivee_ou_depart = "Départ enregistré : " + current_time.strftime('%H:%M:%S')
                else:
                    # Sinon, c'est une arrivée
                    shift.heures_arrivees.append(current_time.strftime('%H:%M:%S'))
                    arrivee_ou_depart = "Arrivée enregistrée : " + current_time.strftime('%H:%M:%S')

            shift.save()
            # 🔥 Vérifier si un shift est prévu pour cet employé aujourd'hui
            team_planning = TeamPlanning.objects.filter(Employe=employe, date=current_date).first()

            if team_planning:
                # 🔥 Associer le badge shift au TeamPlanning existant
                team_planning.users_badged_shift = shift
                team_planning.save()
            else:
                # 🔥 Si aucun planning n'existe, en créer un automatiquement et lui faire avoir une apparence particulière par la suite
                TeamPlanning.objects.create(
                    Employe=employe,
                    date=current_date,
                    Heurededébut=current_time,
                    heuredefin="20:00",
                    duréepause="00:30",  # Valeur par défaut
                    Poste=employe.Poste,  # Par défaut
                    is_unscheduled = True,
                    users_badged_shift=shift
                )
            return JsonResponse({'status': 'success', 'message': f'{arrivee_ou_depart} pour {employe.firstname} {employe.name}'})

        except Employe.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Code PIN incorrect ou employé non trouvé dans votre entreprise'})

    return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)

def success(request):
   return render(request, 'base/success.html')

def home(request):
    employe = Employe.objects.all()
    context = {'employe' : employe}
    return render(request, 'base/home.html', context)

def schedules_page(request):
    # Your logic for the schedules page goes here
    return render(request, 'base/schedules_page.html')

def team_members_page(request):
    if request.user.is_authenticated:
        # Access the 'entreprise' attribute of the user
        user_entreprise = request.user.entreprise
        if user_entreprise is None:
            # Do something with user_entreprise
            return HttpResponse("L'administrateur doit vous assigner une entreprise")
        else:
            pass #Normal behaviour, the page is displayed
    else:
        return HttpResponse("Vous devez vous connecter pour accèder à cette page")
    employe = Employe.objects.filter(EntrepriseRattachée=user_entreprise)
    context = {'employe' : employe}
    return render(request, 'base/team_members_page.html', context)

def update_shift(request):
    if request.method == "POST":
        shift_id = request.POST.get("shift_id")
        new_employe_id = request.POST.get("new_employe_id")
        new_poste = request.POST.get("new_poste")
        new_date = request.POST.get("new_date")
        new_start_time = request.POST.get("new_start_time")
        new_end_time = request.POST.get("new_end_time")
        new_pause_duration = request.POST.get("new_pause_duration")
        new_note = request.POST.get("new_note")
        action = request.POST.get("actionButton")
        employe = get_object_or_404(Employe, id=new_employe_id)

        if action == "copier":
            try:
                new_shift = TeamPlanning.objects.create(
                    Employe=employe,
                    date=new_date,
                    Heurededébut=new_start_time,
                    heuredefin=new_end_time,
                    duréepause=new_pause_duration,
                    is_overtime=False,
                    Poste=employe.Poste,
                    note=new_note if new_note != "undefined" else ""
                )
                new_shift.save()
                #messages.success(request, "Shift moved successfully!")
            except Exception as e:
                messages.error(request, f"❌ Error: {str(e)}")
        elif action == "deplacer":
            try:
                shift = get_object_or_404(TeamPlanning, id=shift_id)
                shift.delete()
                new_shift = TeamPlanning.objects.create(
                    Employe=employe,
                    date=new_date,
                    Heurededébut=new_start_time,
                    heuredefin=new_end_time,
                    duréepause=new_pause_duration,
                    is_overtime=False,
                    Poste=employe.Poste,
                    note=new_note if new_note != "undefined" else ""
                )
                new_shift.save()
                #messages.success(request, "Shift moved successfully!")
            except Exception as e:
                messages.error(request, f"❌ Error: {str(e)}")
                
    date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
    return redirect('planning_with_params', year=date_obj.year, week=date_obj.isocalendar()[1])
    return redirect("planning")  # 🔄 Reload page

def planning(request, year=None, week=None):
    # Générer les semaines pour 2025 et 2026
    #generate_weeks_for_year(2025)
    #generate_weeks_for_year(2026)
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        # Access the 'entreprise' attribute of the user
        user_entreprise = request.user.entreprise

        if user_entreprise is None:
            # Do something with user_entreprise
            return HttpResponse("L'administrateur doit vous assigner une entreprise")
        else:
            pass #Normal behaviour, the page is displayed
    else:
        return HttpResponse("Vous devez vous connecter pour accèder à cette page")
    # Handles a date picked from datepicker
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        year, week, _ = selected_date.isocalendar()
    # end of datepicker code 
    if not year or not week:
        # Get the current week if no year and week are provided
        today = datetime.now()
        year, week, _ = today.isocalendar()

    # Calculate the start and end dates for the given week
    start_date = datetime.fromisocalendar(int(year), int(week), 1)
    end_date = start_date + timedelta(days=6)

    # Calculate previous and next week information
    prev_week = int(week) - 1 if int(week) > 1 else 52
    prev_year = int(year) - 1 if int(week) == 1 else int(year)
    next_week = int(week) + 1 if int(week) < 52 else 1
    next_year = int(year) + 1 if int(week) == 52 else int(year)

    # Generate a list of days in the week
    days = [start_date + timedelta(days=i) for i in range(7)]

    # You should query your database to get the schedule data for the specified week
    # For the sake of this example, let's assume you have a list of tasks
    tasks = [
        {'date': start_date + timedelta(days=i), 'tasks': [{'date': start_date + timedelta(days=i), 'task': f'Task {i+1}'}]}
        for i in range(7)
    ]
    #employe = Employe.objects.all() #select the employees that belong to the same entreprise as the user
    employe = Employe.objects.filter(EntrepriseRattachée=user_entreprise)
    teamPlanning = None
    if request.method == 'POST':
        if "action" in request.POST:#This, if true, sends to the "Add, edit, delete, add absence single shift route"
            form = ModifyPlanningForm(request.POST, instance=teamPlanning)
            print(form)
            if form.is_valid():
                print(form.cleaned_data)
                if form.cleaned_data['action'] == "EditShift":
                    print('editshift path')
                    if 'actionButton' in request.POST:
                        actionButton = request.POST['actionButton']
                        if actionButton == 'edit':
                            print("edit")
                            # Retrieve the TeamPlanning instance by ID
                            myid = form.cleaned_data['shift_Id']
                            team_planning_instance = get_object_or_404(TeamPlanning, pk=myid)
                            team_planning_instance.date = form.cleaned_data['date']
                            team_planning_instance.Poste = form.cleaned_data['Poste']
                            team_planning_instance.Heurededébut = form.cleaned_data['Heurededébut']
                            team_planning_instance.heuredefin = form.cleaned_data['heuredefin']
                            team_planning_instance.duréepause = form.cleaned_data['duréepause']#duree_pause_timedelta
                            team_planning_instance.note = form.cleaned_data['note']
                            team_planning_instance.save()
                        elif actionButton == 'delete':
                            print("delete")
                            # Retrieve the TeamPlanning instance by ID
                            myid = form.cleaned_data['shift_Id']
                            team_planning_instance = get_object_or_404(TeamPlanning, pk=myid)
                            # Delete the instance
                            team_planning_instance.delete()
                elif form.cleaned_data['action'] == "AddShift":
                    team_planning_instance = form.save(commit=False) #create a TeamPlanning instance without immediately saving it to the database.
                    # Manually set the fields that are outside the Meta class
                    team_planning_instance.date = form.cleaned_data['date']
                    team_planning_instance.Heurededébut = form.cleaned_data['Heurededébut']
                    team_planning_instance.heuredefin = form.cleaned_data['heuredefin']
                    # Handle duréepause conversion to timedelta if necessary
                    # Example: if duréepause is represented as "HH:MM" string
                    # duree_pause_time = datetime.strptime(form.cleaned_data['duréepause'], '%H:%M')
                    # duree_pause_timedelta = timedelta(hours=duree_pause_time.hour, minutes=duree_pause_time.minute)
                    team_planning_instance.duréepause = form.cleaned_data['duréepause']#duree_pause_timedelta
                    team_planning_instance.is_overtime = form.cleaned_data['checkbox_field_heuresup']
                    team_planning_instance.note = form.cleaned_data['note']
                    team_planning_instance.save()
                elif form.cleaned_data['action'] == "NouvelleAbsence":
                    print("xxxxxxxxxxxxxxxxxxxxxxx ITS HERE new absence xxxxxxxxxxxxxxxxxxxxxxxx")
                    team_planning_instance = form.save(commit=False) #create a NewAbsence instance without immediately saving it to the database.
                    # Manually set the fields that are outside the Meta class
                    team_planning_instance.date = form.cleaned_data['date']
                    team_planning_instance.Heurededébut = form.cleaned_data['Heurededébut']
                    team_planning_instance.heuredefin = form.cleaned_data['heuredefin']
                    team_planning_instance.duréepause = form.cleaned_data['duréepause']#duree_pause_timedelta
                    team_planning_instance.is_absence = True
                    team_planning_instance.TypeAbsence = form.cleaned_data['TypeAbsence']
                    team_planning_instance.note = form.cleaned_data['note']
                    boolDeleteOtherShifts = form.cleaned_data['checkbox_field']
                    dateFinAbsence = form.cleaned_data['second_date']
                    ProcessNewAbsence(team_planning_instance, dateFinAbsence, boolDeleteOtherShifts)
                    team_planning_instance.save()
                    team_planning_instance.delete() #on supprime pour pas avoir double copie du premier jour
                modification_date = form.cleaned_data['date']
                return redirect('planning_with_params', year=modification_date.year, week=modification_date.isocalendar()[1])
                #return redirect('planning')  # Redirect to the desired page
            else:
                print("form is not valid : ")
                print(form.errors)
        else : #add an if later, this will be the multiple shifts copy/delete route
            print(request.POST)
            action = request.POST.get('actionButton')
            if action == 'ValidateCopyMultipleShifts':
                selectionform = SelectionForm(request.POST)
                print("xxxxxxxxxxxxxxxxxxxxxxx ITS HERE COPYMULTIPLE xxxxxxxxxxxxxxxxxxxxxxxx")
                print(selectionform)
                ProcessMultipleShifts(selectionform.cleaned_data['employees'],
                                          selectionform.cleaned_data['weeks'], selectionform.cleaned_data['days'], week, action, selectionform.cleaned_data['year_to_copy_from'])
            elif action == 'ValidateDeleteMultipleShifts':
                selectionform = SelectionForm(request.POST)
                print("xxxxxxxxxxxxxxxxxxxxxxx ITS HERE DELETEMULTIPLE xxxxxxxxxxxxxxxxxxxxxxxx")
                print(selectionform)
                ProcessMultipleShifts(selectionform.cleaned_data['employees'],
                                          selectionform.cleaned_data['weeks'], selectionform.cleaned_data['days'], week, action, selectionform.cleaned_data['year_to_copy_from'])
            return redirect('planning')  # Redirect to the desired page
    else: #following else code gets executed when user clicks on "Planning" on their browser
        form = ModifyPlanningForm(instance=teamPlanning)  # Pass employe_id here
        selectionform = SelectionForm()
    #Code to render shifts:
    shifts_by_emp_and_day = {}
    for emp in employe:
        shifts_by_day = {}
        for day in days:
            shifts = emp.teamplanning_set.filter(date=day)
            if not shifts.exists():
                continue
            shifts_by_day[day] = shifts
            #print(shifts)
        shifts_by_emp_and_day[emp.id] = shifts_by_day
    # if len(shifts_by_day) > 0:
    #     print(shifts_by_day)
    #weeks = Week.objects.all() on va travailler uniquement sur les semaines de l'année en cours 
    # Calculate the date 3 days after start_date
    date_after_three_days = start_date + timedelta(days=3)
    # Extract the year of that date
    year_of_interest = date_after_three_days.year
    # Filter weeks based on the calculated year
    weeks = Week.objects.filter(year=year_of_interest)
    context = {
        'days': days,
        'tasks': tasks,
        'start_date': start_date,
        'end_date': end_date,
        'prev_week': prev_week,
        'prev_year': prev_year,
        'next_week': next_week,
        'next_year': next_year,
        'employe' : employe,
        'form' : form,
        'shifts_by_emp_and_day': shifts_by_emp_and_day,
        'weeks': weeks,
        'selectionform' : selectionform,
    }
    return render(request, 'base/planning.html', context)

def create_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_members_page')  # Redirect to the employee list page
    else:
        form = EmployeForm(user=request.user)

    return render(request, 'base/create_employe.html', {'form': form})

def modify_employe(request, employe_id):
    employe = get_object_or_404(Employe, pk=employe_id)

    if request.method == 'POST':
        form = ModifyEmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('team_members_page')  # Redirect to the employee list page
    else:
        form = ModifyEmployeForm(instance=employe)  # Pass employe_id here

    return render(request, 'base/modify_employe.html', {'form': form, 'employe_id': employe_id})

@require_POST
@csrf_protect
def delete_employe(request):
    data = json.loads(request.body)
    employe_id = data.get('employe_id')
    employe = get_object_or_404(Employe, pk=employe_id)
    employe.delete()
    return JsonResponse({'deleted': True})

def admin_approval(request):
    context = {}
    return render(request, 'base/admin.html', context)

def ProcessNewAbsence(team_planning_instance, dateFinAbsence, boolDeleteOtherShifts):#emp : Employe.id, dateDebut, dateFin, heuredebut, heurefin, pause, typeAbsence, supressionAutreShifts, Note):
    # Ensure the date range is valid
    if dateFinAbsence and dateFinAbsence >= team_planning_instance.date:
        current_date = team_planning_instance.date
        end_date = dateFinAbsence

        # Iterate through each date in the range
        while current_date <= end_date:
            # If required, delete other shifts on the same day
            if boolDeleteOtherShifts:
                TeamPlanning.objects.filter(
                    Employe=team_planning_instance.Employe,
                    date=current_date
                ).delete()

            # Create a new instance for the current date
            new_instance = TeamPlanning.objects.create(
                Employe=team_planning_instance.Employe,
                date=current_date,
                Heurededébut=team_planning_instance.Heurededébut,
                heuredefin=team_planning_instance.heuredefin,
                duréepause=team_planning_instance.duréepause,
                Poste=team_planning_instance.Poste,
                note=team_planning_instance.note,
                is_absence=True,  # Mark as absence
                TypeAbsence=team_planning_instance.TypeAbsence
            )

            # Increment the date
            current_date += timedelta(days=1)

        print(f"Absence instances created from {team_planning_instance.date} to {dateFinAbsence}")
    else:
        print("Invalid date range: End date must be after or equal to start date.")

def ProcessMultipleShifts(EmpidList, WeekList, DayListPreProcessed, CurrentWeekShifts, action, year_to_copy_from):#problème d'année non prise en compte (et copier des shift de semaine 51,52 2024 à 1,2 2025 poserait probleme si mal implanté
    id_list = [int(id_str) for id_str in EmpidList.split(',')]
    weeks_list = [int(id_str) for id_str in WeekList.split(',')]
    DayList = DayListPreProcessed.split(',')
    for emp in id_list:
        for week in weeks_list:
            for day in DayList:
                if action == 'ValidateCopyMultipleShifts':
                    CopyOneEmployeOneShiftOneWeek(emp, week, day, CurrentWeekShifts, year_to_copy_from) #add current week in here so we know what to copy
                elif action == 'ValidateDeleteMultipleShifts':
                    DeleteOneEmployeOneShiftOneWeek(emp, week, day, CurrentWeekShifts, year_to_copy_from)
    pass

def CopyOneEmployeOneShiftOneWeek(emp : Employe.id, week : Week, DaysToCopy, CurrentWeek, year_to_copy_from): # problème de gestion des années supprimer ce commentaire lorsque résolu
    employe = get_object_or_404(Employe, pk=emp)
    weekToCopyTo = get_object_or_404(Week, week_number=week, year = year_to_copy_from)
    weekToCopyFrom = get_object_or_404(Week, week_number=CurrentWeek, year = year_to_copy_from)
    days = weekToCopyFrom.get_week_days()
    DaysToCopyTo = weekToCopyTo.get_week_days()
    shifts_by_day = {}
    i = 0
    for day in days:
        i += 1
        if 'Lundi' not in DaysToCopy and i == 1:
            continue
        if 'Mardi' not in DaysToCopy and i == 2:
            continue
        if 'Mercredi' not in DaysToCopy and i == 3:
            continue
        if 'Jeudi' not in DaysToCopy and i == 4:
            continue
        if 'Vendredi' not in DaysToCopy and i == 5:
            continue
        if 'Samedi' not in DaysToCopy and i == 6:
            continue
        if 'Dimanche' not in DaysToCopy and i == 7:
            continue
        shifts = employe.teamplanning_set.filter(date=day)
        if not shifts.exists():
            continue
        #shifts_by_day[day] = shifts
        print(shifts)
        for shift in shifts:
            team_planning_instance = TeamPlanning(
                Employe=shift.Employe,
                date=DaysToCopyTo[i-1], #Lundi est à [0] alors que i débute à 1 etc.
                Heurededébut=shift.Heurededébut,
                heuredefin=shift.heuredefin,
                duréepause=shift.duréepause,
                Poste=shift.Poste,
                note=shift.note,
                    ) #fill stuff here
            team_planning_instance.save()

def generate_weeks_for_year(year):
    """
    Génère toutes les semaines pour une année donnée en respectant la norme ISO 8601.
    """

    # Boucle pour les semaines 1 à 53
    for week_number in range(1, 54):  # Maximum 53 semaines
        try:
            # Trouver le premier jour de cette semaine ISO
            first_jeudi_of_week = date.fromisocalendar(year, week_number, 4)  # Lundi de la semaine
            first_day_of_week = first_jeudi_of_week - timedelta(days=3)  # Lundi de la semaine 1

        except ValueError:
            break  # Stopper si la semaine n'existe pas (ex: semaine 53 inexistante)

        # Créer ou mettre à jour la semaine dans la base de données
        try:
            o = Week.objects.filter(week_number=1, year=2025)
            print(o)
            week, created = Week.objects.get_or_create(
                week_number=week_number,
                year=year,
                defaults={'first_day': first_day_of_week}
            )
            if created:
                print(f"✅ Week {week_number} ({year}) created successfully: {first_day_of_week}")
            else:
                print(f"⚠️ Week {week_number} ({year}) already exists with first_day: {week.first_day}")

        except Exception as e:
            print(f"❌ ERROR: Failed to create Week {week_number} ({year}).")
            print(f"   → first_day: {first_day_of_week}")
            print(f"   → Exception: {e}")



def DeleteOneEmployeOneShiftOneWeek(emp : Employe.id, week : Week, DaysToDelete, CurrentWeek, year_to_copy_from):
    employe = get_object_or_404(Employe, pk=emp)
    weekToDeleteTo = get_object_or_404(Week, week_number=week, year = year_to_copy_from)
    weekToCopyFrom = get_object_or_404(Week, week_number=CurrentWeek, year = year_to_copy_from)
    days = weekToCopyFrom.get_week_days()
    DaysToDeleteTo = weekToDeleteTo.get_week_days()
    shifts_by_day = {}
    if 'Lundi' in DaysToDelete:
        shifts = employe.teamplanning_set.filter(date=DaysToDeleteTo[0])
        if not shifts.exists():
            return
        for shift in shifts:
            print(shift)
            shift.delete()
    if 'Mardi' in DaysToDelete:
        shifts = employe.teamplanning_set.filter(date=DaysToDeleteTo[1])
        if not shifts.exists():
            return
        for shift in shifts:
            print(shift)
            shift.delete()
    if 'Mercredi' in DaysToDelete:
        shifts = employe.teamplanning_set.filter(date=DaysToDeleteTo[2])
        if not shifts.exists():
            return
        for shift in shifts:
            print(shift)
            shift.delete()
    if 'Jeudi' in DaysToDelete:
        shifts = employe.teamplanning_set.filter(date=DaysToDeleteTo[3])
        if not shifts.exists():
            return
        for shift in shifts:
            print(shift)
            shift.delete()
    if 'Vendredi' in DaysToDelete:
        shifts = employe.teamplanning_set.filter(date=DaysToDeleteTo[4])
        if not shifts.exists():
            return
        for shift in shifts:
            print(shift)
            shift.delete()
    if 'Samedi' in DaysToDelete:
        shifts = employe.teamplanning_set.filter(date=DaysToDeleteTo[5])
        if not shifts.exists():
            return
        for shift in shifts:
            print(shift)
            shift.delete()
    if 'Dimanche' in DaysToDelete:
        shifts = employe.teamplanning_set.filter(date=DaysToDeleteTo[6])
        if not shifts.exists():
            return
        for shift in shifts:
            print(shift)
            shift.delete()