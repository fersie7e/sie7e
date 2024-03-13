from django.urls import path

from . import views

urlpatterns = [
    path("<int:page>", views.indexdiets, name="indexdiets"),
    path("new/", views.nuevo_cliente, name="nuevo_cliente"),
    path("revision/<int:id_cliente>", views.ficha_revision, name="ficha_revision"),
    path("pdf_revision/<int:id_revision>", views.pdf_revision, name="pdf_revision"),
    path("revision/data/<int:id_cliente>", views.ChartDataDiets.as_view()),
]