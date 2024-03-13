from django import forms
from .models import Cliente

class ClientForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 
            'apellidos', 
            'f_inicio', 
            'f_nacimiento', 
            'direccion', 
            'telefono', 
            'fumador', 
            'activo', 
            'transito_intestinal_normal',
            'hidratacion',
            'alergias',
            'tratamientos',
            'habitos',
            'observaciones',
            'altura' 
        ]

