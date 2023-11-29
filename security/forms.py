from django import forms
from .models import Shift


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = [
            'venue',
            'shift_provider',
            'date'
        ]