from django.shortcuts import render
from .models import Venue, Shift, Employee, Provider, Service
from .forms import ShiftForm
import datetime
# Create your views here.

YEARS_CHOICE = []
for year in range(2022, (datetime.datetime.now().year+3)):
    YEARS_CHOICE.append(str(year))

CURRENT_MONTH = str(datetime.datetime.now().month)
CURRENT_YEAR = str(datetime.datetime.now().year)
MONTH31 = [1, 3, 5, 7, 8, 10, 12]
MONTHDICT = {
    "1":'JAN',
    "2":'FEB',
    "3":'MAR',
    "4":'APR',
    "5":'MAY',
    "6":'JUN',
    "7":'JUL',
    "8":'AUG',
    "9":'SEP',
    "10":'OCT',
    "11":'NOV',
    "12":'DIC'
}


def shift_filter(month, year):
    init_date = year + "-" + month + "-01"
    if month in MONTH31:
        end_date = year + "-" + month + "-31"
    else:
        end_date = year + "-" + month + "-30"
    shift_data = Shift.objects.filter(date__range=[init_date, end_date])
    return shift_data


def index(request):
    shift_data = shift_filter(CURRENT_MONTH, CURRENT_YEAR)

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
        "years": YEARS_CHOICE,
        "month": CURRENT_MONTH,
        "year": CURRENT_YEAR,
        "month_text": MONTHDICT[CURRENT_MONTH],
        "monthdict": MONTHDICT.items(),
        "edit": False,
        "service_selected": False,
    })



def filtershift(request, month=CURRENT_MONTH, year=CURRENT_YEAR):
    shift_data = shift_filter(month, year)

    if request.method == "POST":
        month = request.POST["month"]
        year = request.POST["year"]
        shift_data = shift_filter(month, year)

    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "shifts": shift_data,
        "years": YEARS_CHOICE,
        "month": month,
        "year": year,
        "month_text": MONTHDICT[month],
        "monthdict": MONTHDICT.items(),
        "edit": False,
        "service_selected": False,
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
    month = str(shift.date.month)
    year = str(shift.date.year)
    shift_data = shift_filter(month, year)



    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "services": services,
        "shifts": shift_data,
        "years": YEARS_CHOICE,
        "month": month,
        "year": year,
        "month_text": MONTHDICT[month],
        "monthdict": MONTHDICT.items(),
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
    month = str(shift.date.month)
    year = str(shift.date.year)
    shift_data = shift_filter(month, year)



    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "services": services,
        "shifts": shift_data,
        "years": YEARS_CHOICE,
        "month": month,
        "year": year,
        "month_text": MONTHDICT[month],
        "monthdict": MONTHDICT.items(),
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
    month = str(shift.date.month)
    year = str(shift.date.year)
    shift_data = shift_filter(month, year)



    return render(request, 'security/index.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "services": services,
        "shifts": shift_data,
        "years": YEARS_CHOICE,
        "month": month,
        "year": year,
        "month_text": MONTHDICT[month],
        "monthdict": MONTHDICT.items(),
        "edit": True,
        "editshift": shift,
        "working": working,
        "not_working": not_working,
        "employees": employees,
        "service_selected": True,
    })