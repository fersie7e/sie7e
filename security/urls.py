from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("filter/<str:date>", views.filtershift, name="filtershift"),
    path("addshift/",views.addshift,name="addshift"),
    path("add/<int:shift_id>/", views.addemployee, name="addemployee"),
    path("delete/<int:shift_id>/<int:employee_id>", views.deleteemployeeshift, name="deleteemployeeshift"),
    path("set/<int:shift_id>", views.setservice, name="setservice"),
]