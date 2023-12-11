from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template.loader import render_to_string

from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

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

def get_venues_allowed(user):
    venues = Venue.objects.all()
    venues_allowed = []
    for venue in venues:
        if user in venue.users.all():
            venues_allowed.append(venue)
    return venues_allowed

def get_providers_allowed(user):
    providers = Provider.objects.all()
    providers_allowed = []
    for provider in providers:
        if user in provider.users.all():
            providers_allowed.append(provider)
    return providers_allowed

def get_employees_allowed(user):
    providers = get_providers_allowed(user)
    employees = Employee.objects.all()
    employees_allowed = []
    for employee in employees:
        if  employee.provider in providers:
            employees_allowed.append(employee)
    return employees_allowed

def calc_wages(shifts, providers):
    wages = {}
    salary = 0
    result = []
    for shift in shifts:
        if shift.shift_provider in providers:
            employees = shift.employees.all()
            for employee in employees:
                key = employee.first_name + " " + employee.last_name
                if key in wages:
                    wages[key] = [wages.get(key)[0] + 1, 0]
                else:
                    wages[key] = [1,0]
        salary = shift.service_provided.servicefee.salary
    result.append(wages)
    result.append(salary)
    return result

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("invoicefilter"))

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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    if request.method == "POST":
        date = request.POST['date']
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = ShiftForm() 
    
    return HttpResponseRedirect(reverse("filtershift", args=(date,)))


def setservice(request, shift_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    shift = Shift.objects.get(pk=shift_id)
    if request.method == "POST":
        employee_id = request.POST["employee"]
        employee = Employee.objects.get(pk=employee_id)
        shift.employees.add(employee)
    
    return HttpResponseRedirect(reverse("setservice", args=(shift_id,)))


def deleteemployeeshift(request, shift_id, employee_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    shift = Shift.objects.get(pk=shift_id)
    employee = Employee.objects.get(pk=employee_id)
    shift.employees.remove(employee)
    
    return HttpResponseRedirect(reverse("setservice", args=(shift_id,)))

    
def invoiceGen(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("invoicefilter"))
    
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
    
    return render(request, 'security/invoices/invoice_gen.html', {
        "venues": Venue.objects.all(),
        "providers": Provider.objects.all(),
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
        "success": success,
    })


def invoicefilter(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    invoices_filtered = []
    venues_allowed = get_venues_allowed(request.user)
    providers_allowed = get_providers_allowed(request.user)


    month = CURRENT_MONTH
    year = CURRENT_YEAR
    if request.method == "POST":
        month = request.POST['month']
        year = request.POST['year']
    invoices = Invoice.objects.filter(year=year, month=month)

    for invoice in invoices:
        if providers_allowed:
            if invoice.invoice_provider in providers_allowed:
                if invoice.invoice_venue in venues_allowed:
                    invoices_filtered.append(invoice)
        else:
            if invoice.invoice_venue in venues_allowed:
                invoices_filtered.append(invoice)

    return render(request, 'security/invoices/invoice_filter.html', {
        "invoices": invoices_filtered,
        "month": month,
        "year": year,
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
    })


def invoicedetail(request, invoice_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    invoice = Invoice.objects.get(pk=invoice_id)
    shifts = invoice.shifts.all()
    total_shifts = 0
    for shift in shifts:
        total_shifts += shift.employees.count()
    
    return render(request, 'security/invoices/invoice_detail.html', {
        "invoice": invoice,
        "total_shifts": total_shifts,
    })


def invoicepdf(request, invoice_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    invoice = Invoice.objects.get(pk=invoice_id)
    shifts = invoice.shifts.all()
    total_shifts = 0
    for shift in shifts:
        total_shifts += shift.employees.count()
    context = {
        "invoice": invoice,
        "total_shifts": total_shifts,
    }
    html = render_to_string("security/invoices/invoice_pdf.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; invoice.pdf"

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response


def wagesfilter(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    providers_allowed = get_providers_allowed(request.user)
    if not providers_allowed:
        return HttpResponseRedirect(reverse("invoicefilter"))
    
    month = CURRENT_MONTH
    year = CURRENT_YEAR
    if request.method == "POST":
        month = request.POST['month']
        year = request.POST['year']
        provider_id = request.POST['wages_provider']
        provider = Provider.objects.get(pk=provider_id)
        shifts = Shift.objects.filter(date__year=year, date__month=month, shift_provider=provider)
    else:
        shifts = Shift.objects.filter(date__year=year, date__month=month)
    
    total_wages = 0

    result = calc_wages(shifts=shifts, providers=providers_allowed)
    wages = result[0]

    for name,list in wages.items():
        list[1] = int(list[0]) * result[1]
        wages[name] = list
        total_wages += list[1]
    
    return render(request, 'security/wages/wages_filter.html', {
        "month": month,
        "year": year,
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
        "wages": wages,
        "providers": providers_allowed,
        "total_wages": total_wages,
    })

def wagesfilterpdf(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    providers_allowed = get_providers_allowed(request.user)
    if not providers_allowed:
        return HttpResponseRedirect(reverse("invoicefilter"))
    
    month = CURRENT_MONTH
    year = CURRENT_YEAR
    
    
    return render(request, 'security/wages/wages_filter_pdf.html', {
        "month": month,
        "year": year,
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
        "providers": providers_allowed,
    })

def wagespdf(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    providers_allowed = get_providers_allowed(request.user)
    if not providers_allowed:
        return HttpResponseRedirect(reverse("invoicefilter"))
    
    provider = None
    month = CURRENT_MONTH
    year = CURRENT_YEAR
    if request.method == "POST":
        month = request.POST['month']
        year = request.POST['year']
        provider_id = request.POST['wages_provider']
        provider = Provider.objects.get(pk=provider_id)
        shifts = Shift.objects.filter(date__year=year, date__month=month, shift_provider=provider)
    else:
        shifts = Shift.objects.filter(date__year=year, date__month=month)
  
    total_wages = 0
    result = calc_wages(shifts=shifts, providers=providers_allowed)
    wages = result[0]

    for name,list in wages.items():
        list[1] = int(list[0]) * result[1]
        wages[name] = list
        total_wages += list[1]
    
    context = {
        "month": month,
        "year": year,
        "months": MONTHS,
        "year_choice": YEARS_CHOICE,
        "wages": wages,
        "provider": provider,
        "providers": providers_allowed,
        "total_wages": total_wages,
    }
    html = render_to_string("security/wages/wages_pdf.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; invoice.pdf"

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response
    

def wagesemployee(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    providers_allowed = get_providers_allowed(request.user)
    if not providers_allowed:
        return HttpResponseRedirect(reverse("invoicefilter"))
    
    month = CURRENT_MONTH
    year = CURRENT_YEAR
    employees = get_employees_allowed(request.user)
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
    
    return render(request, 'security/wages/wages_employee.html', {
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

