from django.shortcuts import render
from .models import Venue, Shift, Employee, Provider, Service
from .forms import ShiftForm
import datetime
# Create your views here.


CURRENT_MONTH = str(datetime.datetime.now().month)
CURRENT_YEAR = str(datetime.datetime.now().year)
TODAY = datetime.date.today()

def index(request):
    shift_data = Shift.objects.filter(date=TODAY)

    if request.method == "POST":
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = ShiftForm()


    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "shifts": shift_data,
        "edit": False,
        "service_selected": False,
        "date":TODAY,
    })



def filtershift(request, date=TODAY):
    if request.method == "POST":
        datesent = request.POST["dateSearch"] 
        month = int(datesent[0:2])
        day = int(datesent[3:5])
        year = int(datesent[6:10])
        date = datetime.date(year,month,day)
    shift_data = Shift.objects.filter(date=date)
    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "shifts": shift_data,
        "edit": False,
        "service_selected": False,
        "date": date
    })


def setservice(request, shift_id):
    shift = Shift.objects.get(pk=shift_id)
    provider = shift.shift_provider
    employees = Employee.objects.filter(provider=provider)
    services = provider.services.all()

    if shift.service_provided:
        service = shift.service_provided
        service_selected = True
    else:
        if request.method == "POST":
            service_id = request.POST["service"]
            service = Service.objects.get(pk=service_id)
            shift.service_provided = service
            shift.save()
            service_selected = True
        else:
            service_selected = False
            service = services

    working = shift.employees.filter(provider=provider)
    not_working = []
    for emp in employees:
        if emp not in working and emp.provider == provider:
            not_working.append(emp)
    shift_data = Shift.objects.filter(date=shift.date)


    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "services": services,
        "shifts": shift_data,
        "edit": True,
        "editshift": shift,
        "working": working,
        "not_working": not_working,
        "employees": employees,
        "service_selected": service_selected,
        "service": service,
    })

def addemployee(request, shift_id):
    shift = Shift.objects.get(pk=shift_id)
    provider = shift.shift_provider
    employees = Employee.objects.filter(provider=provider)
    services = provider.services.all()


    if request.method == "POST":
        employee_id = request.POST["employee"]
        employee = Employee.objects.get(pk=employee_id)
        shift.employees.add(employee)

    working = shift.employees.filter(provider=provider)
    not_working=[]
    for emp in employees:
        if emp not in working and emp.provider == provider:
            not_working.append(emp)
    shift_data = Shift.objects.filter(date=shift.date)



    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "services": services,
        "shifts": shift_data,
        "edit": True,
        "editshift": shift,
        "working": working,
        "not_working": not_working,
        "employees": employees,
        "service_selected": True,
    })


def deleteemployeeshift(request, shift_id, employee_id):
    shift = Shift.objects.get(pk=shift_id)
    provider = shift.shift_provider
    services = provider.services.all()
    employees = Employee.objects.filter(provider=provider)
    employee = Employee.objects.get(pk=employee_id)

    shift.employees.remove(employee)

    working = shift.employees.filter(provider=provider)
    not_working = []
    for emp in employees:
        if emp not in working and emp.provider == provider:
            not_working.append(emp)
    shift_data = Shift.objects.filter(date=shift.date)



    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "services": services,
        "shifts": shift_data,
        "edit": True,
        "editshift": shift,
        "working": working,
        "not_working": not_working,
        "employees": employees,
        "service_selected": True,
    })