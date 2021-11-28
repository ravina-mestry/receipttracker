from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Receipt
from .forms import ReceiptForm

def home(request):
    return render(request, 'receipts/home.html', {})

def receipt_list(request):
    receipt_list = Receipt.objects.all().order_by('-id')
    return render(request, 'receipts/receipt_list.html', {'receipt_list':receipt_list})

def receipt_add(request):
    if request.method == "POST":
        form = ReceiptForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, ("Receipt Addition Successful!"))
            return redirect('receipt-list')
        else:
            messages.success(request, ("Receipt Addition Error! Please try again!"))
    else:
        form = ReceiptForm
    return render(request, 'receipts/receipt_add.html', {'form':form})
