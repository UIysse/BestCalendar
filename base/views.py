from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import json
from django.http import JsonResponse, HttpResponse
from .models import Employe, TeamPlanning
from .forms import EmployeForm, ModifyEmployeform, ModifyPlanningForm, ContactForm
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
    # Your logic for the team members page goes here
    employe = Employe.objects.all()
    context = {'employe' : employe}
    return render(request, 'base/team_members_page.html', context)

def planning(request, year=None, week=None):
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
    employe = Employe.objects.all()
    teamPlanning = None
    if request.method == 'POST':
        form = ModifyPlanningForm(request.POST, instance=teamPlanning)
        print(form)
        if form.is_valid():
            if form.cleaned_data['action'] == "EditShift":
                print('editshift path')
                if 'actionButton' in request.POST:
                    actionButton = request.POST['actionButton']
                    if actionButton == 'edit':
                        print("edit")
                    elif actionButton == 'delete':
                        print("delete")
                        # Retrieve the TeamPlanning instance by ID
                        myid = form.cleaned_data['shift_Id']
                        teamplanning_instance = get_object_or_404(TeamPlanning, pk=myid)
                        # Delete the instance
                        teamplanning_instance.delete()
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
    else: #following else code gets executed when user clicks on "Planning" on their browser
        form = ModifyPlanningForm(instance=teamPlanning)  # Pass employe_id here
    #Code to render shifts:
    shifts_by_emp_and_day = {}
    for emp in employe:
        shifts_by_day = {}
        for day in days:
            shifts = emp.teamplanning_set.filter(date=day)
            if not shifts.exists():
                continue
            shifts_by_day[day] = shifts
            print(shifts)
        shifts_by_emp_and_day[emp.id] = shifts_by_day
    print(shifts_by_day)
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
    }
    return render(request, 'base/planning.html', context)

def create_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_members_page')  # Redirect to the employee list page
    else:
        form = EmployeForm()

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