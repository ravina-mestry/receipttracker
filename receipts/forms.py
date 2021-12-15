from django import forms
from django.forms import ModelForm
from .models import Receipt

# define ReceiptForm fields and their order to be shown on add receipt page.
class ReceiptForm(ModelForm):
    class Meta:
        model = Receipt
        fields = ('name', 'date_receipt', 'vendor_name', 'amount_total')
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'date_receipt': forms.TextInput(attrs={'class':'form-control'}),
            'vendor_name': forms.TextInput(attrs={'class':'form-control'}),
            'amount_total': forms.NumberInput(attrs={'step':'0.01', 'min':'0.10', 'class':'form-control'}),
        }
