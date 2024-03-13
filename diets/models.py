from django.db import models

# Create your models here.

HIDRATACION = (
    ("Más de 1,5 litros diarios", "Más de 1,5 litros diarios"),
    ("Menos de 1,5 litros diarios","Menos de 1,5 litros diarios")
)

COMIDAS = (
    ("Desayuno","Desayuno"),
    ("Media mañana","Media mañana"),
    ("Almuerzo","Almuerzo"),
    ("Merienda","Merienda"),
    ("Cena","Cena"),
    ("Post-cena","Post-cena"),
    )
    

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    f_inicio = models.DateField(default=None)
    f_nacimiento = models.DateField()
    direccion = models.CharField(max_length=150)
    telefono = models.CharField(max_length=100)
    fumador = models.BooleanField(default=False)
    activo = models.BooleanField(default=False)
    transito_intestinal_normal = models.BooleanField(default=False)
    hidratacion = models.CharField(max_length=100, choices=HIDRATACION)
    alergias = models.TextField(blank=True, null=True)
    tratamientos = models.TextField(blank=True, null=True)
    habitos = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    altura = models.FloatField(default=0)
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"


class Datos_Revision(models.Model):
    fecha = models.DateField(auto_now_add=True)
    fecha_proxima = models.DateField(null=True, default=None)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, related_name="cliente_revision")
    peso = models.FloatField(null=True)
    contorno_cintura = models.FloatField(null=True)
    contorno_cadera = models.FloatField(null=True)
    grasa_corporal = models.FloatField(null=True)
    IMC = models.FloatField(null=True)
    desayuno = models.TextField(blank=True, null=True)
    media_manana = models.TextField(blank=True, null=True)
    almuerzo = models.TextField(blank=True, null=True)
    merienda = models.TextField(blank=True, null=True)
    cena = models.TextField(blank=True, null=True)
    post_cena = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.pk}->{self.fecha}"
    
