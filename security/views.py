from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Venue, Shift, Employee, Provider, Service, Invoice, Fee
from .forms import ShiftForm
import calendar
import datetime
# Create your views here.

YEARS_CHOICE = []
for year in range(2023, datetime.datetime.now().year + 2):
    YEARS_CHOICE.append(year)

MONTHS = {	'1':'January',
		'2':'February',
		'3':'March',
		'4':'April',
		'5':'May',
		'6':'June',
		'7':'July',
		'8':'August',
		'9':'September',
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
    shift_data = Shift.objects.filter(date__month=month, date__year=year).order_by('date')
    return render(request, 'security/index.html', {
        "shifts": shift_data,
        "cal":cal,
        "year_choice": YEARS_CHOICE,
        "year": year,
        "months": MONTHS,
        "monthtext": monthtext,
        "month": month,
        "days": DAYS,
    })


def filtershift(request, date=TODAY):
    shift_data = Shift.objects.filter(date=date)
    return render(request, 'security/filter.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "shifts": shift_data,
        "service_selected": False,
        "date": date,
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
    return render(request, 'security/set.html', {
        "services": services,
        "editshift": shift,
        "working": working,
        "not_working": not_working,
        "service_selected": service_selected,
        "service": service,
    })


def addemployee(request, shift_id):
    shift = Shift.objects.get(pk=shift_id)
    if request.method == "POST":
        employee_id = request.POST["employee"]
        employee = Employee.objects.get(pk=employee_id)
        shift.employees.add(employee)
    return HttpResponseRedirect(reverse("setservice", args=(shift_id,)))


def deleteemployeeshift(request, shift_id, employee_id):
    shift = Shift.objects.get(pk=shift_id)
    employee = Employee.objects.get(pk=employee_id)
    shift.employees.remove(employee)
    return HttpResponseRedirect(reverse("setservice", args=(shift_id,)))

    
def invoiceGen(request):
    amount = 0
    success = False
    if request.method == "POST":
        month = request.POST['month']
        year = request.POST['year']
        venue_id = request.POST['invoice_venue']
        provider_id = request.POST['invoice_provider']
        venue = Venue.objects.get(pk=venue_id)
        provider = Provider.objects.get(pk=provider_id)
        invoice = Invoice(invoice_venue=venue,
                          invoice_provider=provider,
                          month=month,
                          year=year
                          )
        invoice.save()
        shifts = Shift.objects.filter(venue=venue, shift_provider=provider, date__year=year, date__month=month, invoiced=False)
        for shift in shifts:
            working_number = shift.employees.count()
            fee = shift.service_provided.servicefee.fee
            total_shift = working_number * fee
            amount = amount + total_shift
            invoice.amount = amount
            invoice.shifts.add(shift)
            invoice.save()
            shift.invoiced = True
            shift.invoice_num = invoice.pk
            shift.save()
        success = True
    return render(request, 'security/invoice_gen.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
        "success": success,
    })


def invoicefilter(request):
    month = CURRENT_MONTH
    year = CURRENT_YEAR
    if request.method == "POST":
        month = request.POST['month']
        year = request.POST['year']
    invoices = Invoice.objects.filter(year=year, month=month)
    return render(request, 'security/invoice_filter.html', {
        "invoices": invoices,
        "month": month,
        "year": year,
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
    })


def invoicedetail(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)
    shifts = invoice.shifts.all()
    total_shifts = 0
    for shift in shifts:
        total_shifts += shift.employees.count()
    return render(request, 'security/invoice_detail.html', {
        "invoice": invoice,
        "total_shifts": total_shifts,
    })


def wagesfilter(request):
    month = CURRENT_MONTH
    year = CURRENT_YEAR
    providers = Provider.objects.all()
    if request.method == "POST":
        month = request.POST['month']
        year = request.POST['year']
        provider_id = request.POST['wages_provider']
        provider = Provider.objects.get(pk=provider_id)
        shifts = Shift.objects.filter(date__year=year, date__month=month, shift_provider=provider)
    else:
        shifts = Shift.objects.filter(date__year=year, date__month=month)
    wages = {}
    total_wages = 0
    for shift in shifts:
        employees = shift.employees.all()
        for employee in employees:
            key = employee.first_name + " " + employee.last_name
            if key in wages:
                wages[key] = [wages.get(key)[0] + 1, 0]
            else:
                wages[key] = [1,0]
        salary = shift.service_provided.servicefee.salary
    for name,list in wages.items():
        list[1] = int(list[0]) * salary
        wages[name] = list
        total_wages += list[1]
    return render(request, 'security/wages_filter.html', {
        "shifts": shifts,
        "month": month,
        "year": year,
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
        "wages": wages,
        "providers": providers,
        "total_wages": total_wages,
    })

def wagesemployee(request):
    month = CURRENT_MONTH
    year = CURRENT_YEAR
    employees = Employee.objects.all()
    employee = None
    show = False
    if request.method == "POST":
        month = request.POST['month']
        year = request.POST['year']
        employee_id = request.POST['wages_employee']
        employee = Employee.objects.get(pk=employee_id)
        show = True
    shifts = Shift.objects.filter(date__year=year, date__month=month)
    worked_shifts = []
    for shift in shifts:
        if employee in shift.employees.all():
            worked_shifts.append(shift)
    return render(request, 'security/wages_employee.html', {
        "shifts": shifts,
        "month": month,
        "year": year,
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
        "worked_shifts": worked_shifts,
        "total_shifts": len(worked_shifts),
        "employees": employees,
        "employee": employee,
        "show":show,
    })

