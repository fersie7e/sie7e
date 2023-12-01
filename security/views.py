from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Venue, Shift, Employee, Provider, Service
from .forms import ShiftForm
import calendar
import datetime
# Create your views here.

YEARS_CHOICE = []
for year in range(2022, datetime.datetime.now().year + 4):
    YEARS_CHOICE.append(year)

MONTHS = {	'01':'January',
		'02':'February',
		'03':'March',
		'04':'April',
		'05':'May',
		'06':'June',
		'07':'July',
		'08':'August',
		'09':'September',
		'10':'October',
		'11':'November',
		'12':'December'		}

DAYSLONG = dict(enumerate(calendar.day_name))
DAYS = []
for number,day in DAYSLONG.items():
    DAYS.append(day[0:2])

CURRENT_MONTH = datetime.datetime.now().month
CURRENT_YEAR = datetime.datetime.now().year
TODAY = datetime.date.today()


def parseDate(date):
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    date_formated = datetime.date(year, month, day)
    return date_formated

def index(request):
    shift_data = Shift.objects.filter(date=TODAY)
    cal = calendar.Calendar().monthdatescalendar(CURRENT_YEAR,CURRENT_MONTH)
    monthtext = MONTHS.get(str(CURRENT_MONTH))
    for number,monthname in MONTHS.items():
        if monthname == monthtext:
            month = int(number)
    year = CURRENT_YEAR
    if request.method == "POST":
        month = int(request.POST["month"])
        monthtext = MONTHS.get(str(month))
        year = int(request.POST["year"])
        cal = calendar.Calendar().monthdatescalendar(year,month)


    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "shifts": shift_data,
        "edit": False,
        "service_selected": False,
        "date":TODAY,
        "cal":cal,
        "year_choice": YEARS_CHOICE,
        "year": year,
        "months": MONTHS,
        "monthtext": monthtext,
        "month": month,
        "days": DAYS,
        "date_selected": False,
    })



def filtershift(request, date=TODAY):
    
    date_formatted = parseDate(date)
    month = date_formatted.month
    year = date_formatted.year
    monthtext = MONTHS.get(str(month))
    cal = calendar.Calendar().monthdatescalendar(year,month)
    shift_data = Shift.objects.filter(date=date)

    return render(request, 'security/filter.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "shifts": shift_data,
        "edit": False,
        "service_selected": False,
        "date": date,
        "cal":cal,
        "year_choice": YEARS_CHOICE,
        "year": year,
        "months": MONTHS,
        "monthtext": monthtext,
        "month": month,
        "days": DAYS,
        "date_selected": True,
    })


def addshift(request):
    if request.method == "POST":
        date = request.POST['date']
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = ShiftForm() 
    return HttpResponseRedirect(reverse("filtershift", args=(date,)))



def setservice(request, shift_id):
    shift = Shift.objects.get(pk=shift_id)
    date = shift.date
    month = date.month
    year = date.year
    cal = calendar.Calendar().monthdatescalendar(year,month)
    monthtext = MONTHS.get(str(month))
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


    return render(request, 'security/set.html', {
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
        "date": date,
        "cal":cal,
        "year_choice": YEARS_CHOICE,
        "year": year,
        "months": MONTHS,
        "monthtext": monthtext,
        "month": month,
        "days": DAYS,
        "date_selected": True,
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

    return HttpResponseRedirect(reverse("setservice", args=(shift_id,)))



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

    return HttpResponseRedirect(reverse("setservice", args=(shift_id,)))

    