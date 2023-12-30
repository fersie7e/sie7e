from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("filter/<str:date>", views.filtershift, name="filtershift"),
    path("addshift/",views.addshift,name="addshift"),
    path("add/<int:shift_id>/", views.addemployee, name="addemployee"),
    path("delete/<int:shift_id>/<int:employee_id>", views.deleteemployeeshift, name="deleteemployeeshift"),
    path("set/<int:shift_id>", views.setservice, name="setservice"),
    path("invoice", views.invoiceGen, name="invoicegen"),
    path("invoicefilter/", views.invoicefilter, name="invoicefilter"),
    path("invoicedetail/<int:invoice_id>", views.invoicedetail, name="invoicedetail"),
    path("invoicepdf/<int:invoice_id>", views.invoicepdf, name="invoicepdf"),
    path("wagesfilter/", views.wagesfilter, name="wagesfilter"),
    path("wagesfilterpdf/", views.wagesfilterpdf, name="wagesfilterpdf"),
    path("wagespdf/", views.wagespdf, name="wagespdf"),
    path("wagesemployee/", views.wagesemployee, name="wagesemployee"),
    path("wagesemployeefilter/", views.wagesemployeefilter, name="wagesemployeefilter"),
    path("wagesemployeepdf/", views.wagesemployeepdf, name="wagesemployeepdf"),
    path("setfullmonth/", views.setfullmonth, name="setfullmonth"),
    path("rota/", views.rota, name="rota"),
]