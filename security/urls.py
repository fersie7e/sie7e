from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("filtered", views.filtershift, name="filtershift"),
    path("add/<int:shift_id>/", views.addemployee, name="addemployee"),
    path("delete/<int:shift_id>/<int:employee_id>", views.deleteemployeeshift, name="deleteemployeeshift"),
    path("set/<int:shift_id>", views.setservice, name="setservice"),
]