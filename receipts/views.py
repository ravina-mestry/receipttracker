from django.shortcuts import render
from .models import Receipt

def home(request):
    return render(request, 'receipts/home.html', {})

def receipt_list(request):
    receipt_list = Receipt.objects.all()
    return render(request, 'receipts/receipt_list.html', {'receipt_list':receipt_list})
