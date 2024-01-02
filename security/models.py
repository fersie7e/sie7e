from django.db import models
import datetime
from django.contrib.auth.models import User

# Create your models here.
YEAR_CHOICES = []
for year in range(2021, (datetime.datetime.now().year + 5)):
    YEAR_CHOICES.append((year,year))


class Venue(models.Model):
    users = models.ManyToManyField(User, blank=True, related_name="users")
    commercial_name = models.CharField(max_length=70)
    business_name = models.CharField(max_length=70)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    cif = models.CharField(max_length=10)
    logo = models.ImageField(upload_to="images/", null=True, blank=True, default="sie7e.png")

    def __str__(self):
        return f"{self.commercial_name}"


class Fee(models.Model):
    fee = models.FloatField()
    salary = models.FloatField()

    def __str__(self):
        return f"fee: {self.fee} € - salary: {self.salary} €"


class Service(models.Model):
    name = models.CharField(max_length=50)
    servicefee = models.ForeignKey(Fee, on_delete=models.SET_NULL, null=True, related_name="servicefee")

    def __str__(self):
        return f"{self.name} - {self.servicefee}"


class Provider(models.Model):
    users = models.ManyToManyField(User, blank=True, related_name="usersprovider")
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    cif = models.CharField(max_length=100)
    services = models.ManyToManyField(Service, blank=True, related_name="services")

    def __str__(self):
        return f"{self.name}"


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dni = models.CharField(max_length=15)
    ss = models.CharField(max_length=30)
    ccc = models.CharField(max_length=50)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name="provider")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user_employee")
    phone = models.CharField(max_length=15, default="-")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Shift(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="venue")
    date = models.DateField()
    employees = models.ManyToManyField(Employee, blank=True, related_name="employees")
    shift_provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True, related_name="shift_provider")
    service_provided = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name="service_provided")
    invoiced = models.BooleanField(default=False)
    invoice_num = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.date} - {self.venue}"


class Invoice(models.Model):
    invoice_venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="invoice_venue")
    invoice_provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="invoice_provider")
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    shifts = models.ManyToManyField(Shift, blank=True ,related_name="shifts")
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"{self.month}/{self.year}: {self.invoice_venue} - {self.invoice_provider} Total: {self.amount} €"

