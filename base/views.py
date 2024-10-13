from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import json
from django.http import JsonResponse, HttpResponse
from .models import Employe, TeamPlanning, Week
from .forms import EmployeForm, ModifyEmployeform, ModifyPlanningForm, ContactForm, SelectionForm
from datetime import datetime, timedelta
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

def planning(request, year=None, week=None):
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
                    team_planning_instance.note = form.cleaned_data['note']
                    team_planning_instance.save()
                return redirect('planning')  # Redirect to the desired page
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
                                          selectionform.cleaned_data['weeks'], selectionform.cleaned_data['days'], week, action)
            elif action == 'ValidateDeleteMultipleShifts':
                selectionform = SelectionForm(request.POST)
                print("xxxxxxxxxxxxxxxxxxxxxxx ITS HERE DELETEMULTIPLE xxxxxxxxxxxxxxxxxxxxxxxx")
                print(selectionform)
                ProcessMultipleShifts(selectionform.cleaned_data['employees'],
                                          selectionform.cleaned_data['weeks'], selectionform.cleaned_data['days'], week, action)
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
    weeks = Week.objects.all()
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
        form = ModifyEmployeform(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('team_members_page')  # Redirect to the employee list page
    else:
        form = ModifyEmployeform(instance=employe)  # Pass employe_id here

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

def ProcessMultipleShifts(EmpidList, WeekList, DayListPreProcessed, CurrentWeekShifts, action):
    id_list = [int(id_str) for id_str in EmpidList.split(',')]
    weeks_list = [int(id_str) for id_str in WeekList.split(',')]
    DayList = DayListPreProcessed.split(',')
    for emp in id_list:
        for week in weeks_list:
            for day in DayList:
                if action == 'ValidateCopyMultipleShifts':
                    CopyOneEmployeOneShiftOneWeek(emp, week, day, CurrentWeekShifts) #add current week in here so we know what to copy
                elif action == 'ValidateDeleteMultipleShifts':
                    DeleteOneEmployeOneShiftOneWeek(emp, week, day, CurrentWeekShifts)
    pass

def CopyOneEmployeOneShiftOneWeek(emp : Employe.id, week : Week, DaysToCopy, CurrentWeek):
    employe = get_object_or_404(Employe, pk=emp)
    weekToCopyTo = get_object_or_404(Week, week_number=week)
    weekToCopyFrom = get_object_or_404(Week, week_number=CurrentWeek)
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

def DeleteOneEmployeOneShiftOneWeek(emp : Employe.id, week : Week, DaysToDelete, CurrentWeek):
    employe = get_object_or_404(Employe, pk=emp)
    weekToDeleteTo = get_object_or_404(Week, week_number=week)
    weekToCopyFrom = get_object_or_404(Week, week_number=CurrentWeek)
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