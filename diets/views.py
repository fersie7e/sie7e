from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template.loader import render_to_string

from .forms import ClientForm

import datetime
from dateutil.relativedelta import relativedelta

from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from .models import Cliente, Datos_Revision

from rest_framework.views import APIView
from rest_framework.response import Response

def parseDate(date):
    """Converts a string 'yyyy/mm/dd' into date format

    Args:
        date (str): date to convert

    Returns:
        Date: Value with Date format
    """

    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:])
    date_formated = datetime.date(year, month, day)
    return date_formated
# Create your views here.

def group_list(list, num):
    """transform a list in a list of list of as much item as specified

    Args:
        list (list): list that is going to be procesed
        num (int): number of items per group

    Returns:
        list: list of lists grouped in groups on num
    """
    grouped_list = []
    init = 0
    end = num

    if len(list)%num:
        iterations = int(len(list)/num) + 1
    else:
        iterations = int(len(list))
    for iteration in range(iterations):
        grouped_list.append(list[init:end])
        init = end
        end += num
    return grouped_list

def calcular_edad(id_cliente):
    cliente = Cliente.objects.get(pk=id_cliente)
    edad = relativedelta(datetime.datetime.today(), cliente.f_nacimiento).years
    return edad



def indexdiets(request, page):

    
    num_reg = 5
    
    total_clientes = int(len(Cliente.objects.all()))

    if total_clientes%num_reg == 0:
        total_paginas = int(round(total_clientes/num_reg, 0))
    else:
        total_paginas = int(round(total_clientes/num_reg, 0))+1

    final_pages = [i + 1 for i in range(total_paginas)]
    cantidad_paginas = len(final_pages)
    edades = {}

    if page == 1:
        init = 0
        end = num_reg
        previous = 0
        next = 2
       
    else:
        init = (page*num_reg)-num_reg
        end = page*num_reg
        previous = page-1
        if page == cantidad_paginas:
            next = 0
        else:
            next = page+1
  
    clientes = Cliente.objects.all().order_by('-pk')[init:end]
    
    if request.method == "POST":
        nombre = request.POST['nombre']
        clientes = Cliente.objects.filter(nombre__contains=nombre)

    for cliente in clientes:
        edades[cliente.pk] = calcular_edad(cliente.pk)
    
    return render(request, "diets/indexdiets.html",{
        "clientes": clientes,
        "total_clientes": total_clientes,
        "total_paginas": final_pages,
        "cantidad_paginas": cantidad_paginas,
        "previous": previous,
        "next": next,
        "edades": edades,
        
    })


def nuevo_cliente(request):
    if request.method == "POST":
       
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            form = ClientForm() 
        
    return HttpResponseRedirect(reverse("indexdiets",  args=(1,)) )


def ficha_revision(request, id_cliente):
    fecha = datetime.datetime.today().date
    cliente = Cliente.objects.get(pk=id_cliente)
    revisiones = Datos_Revision.objects.filter(cliente=cliente).order_by('-pk')
    if Datos_Revision.objects.filter(cliente=cliente):
        ultima_revision = Datos_Revision.objects.filter(cliente=cliente).order_by('-pk')[0]
    else:
        ultima_revision = None
    edad = calcular_edad(id_cliente)
    revision = None
    if request.method == "POST":
        if request.POST["revision"]:
            revision = Datos_Revision.objects.get(pk=int(request.POST["revision"]))
            peso = request.POST["peso"]
            revision.contorno_cintura = request.POST["cintura"]
            revision.contorno_cadera = request.POST["cadera"]
            revision.grasa_corporal = request.POST["grasa"]
            revision.IMC = request.POST["imc"]
            revision.fecha_proxima = parseDate(request.POST["f_prox"])
            revision.desayuno = request.POST["desayuno"]
            revision.media_manana = request.POST["media_manana"]
            revision.almuerzo = request.POST["almuerzo"]
            revision.merienda = request.POST["merienda"]
            revision.cena = request.POST["cena"]
            revision.post_cena = request.POST["post_cena"]
            revision.observaciones = request.POST["observaciones"]
            revision.save()
        else:
            peso = request.POST["peso"]
            contorno_cintura = request.POST["cintura"]
            contorno_cadera = request.POST["cadera"]
            grasa_corporal = request.POST["grasa"]
            imc = request.POST["imc"]
            fecha_proxima = parseDate(request.POST["f_prox"])
            desayuno = request.POST["desayuno"]
            media_manana = request.POST["media_manana"]
            almuerzo = request.POST["almuerzo"]
            merienda = request.POST["merienda"]
            cena = request.POST["cena"]
            post_cena = request.POST["post_cena"]
            observaciones = request.POST["observaciones"]
            revision = Datos_Revision(cliente=cliente, fecha=fecha, peso=peso, contorno_cintura=contorno_cintura, contorno_cadera=contorno_cadera, 
                                    grasa_corporal=grasa_corporal, IMC=imc, fecha_proxima=fecha_proxima, desayuno=desayuno, 
                                    media_manana=media_manana, almuerzo=almuerzo, merienda=merienda, cena=cena, post_cena=post_cena,
                                    observaciones=observaciones)
            revision.save()
    
    return render(request, "diets/ficha_revision.html", {
        "cliente": cliente,
        "revision": revision,
        "revisiones": revisiones,
        "edad": edad,
        "ultima_revision": ultima_revision,
        "fecha":fecha,
    })


def pdf_revision(request, id_revision):
    
    revision = Datos_Revision.objects.get(pk=id_revision)
    
    context = {
        "revision": revision,
    }
    html = render_to_string("diets/pdf_revision.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; revision.pdf"

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response


class ChartDataDiets(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, id_cliente, format=None):
        labels = []
        default_items = []
        cintura_items = []
        cadera_items = []
        cliente = Cliente.objects.get(pk=id_cliente)
        revisiones = Datos_Revision.objects.filter(cliente=cliente).order_by('pk')
        for revision in revisiones:
            labels.append(revision.fecha)
            default_items.append(revision.peso)
            cintura_items.append(revision.contorno_cintura)
            cadera_items.append(revision.contorno_cadera)
                
        data = {
                "labels": labels,
                "default": default_items,
                "cintura": cintura_items,
                "cadera": cadera_items,
        }
    
        return Response(data)