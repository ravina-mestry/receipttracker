from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Receipt, ReceiptFile
from .forms import ReceiptForm
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from . import aws

def home(request):
    return render(request, 'receipts/home.html', {})

def receipt_list(request):
    receipt_list = Receipt.objects.all().filter(account_user=request.user.id).order_by('-id')
    p = Paginator(receipt_list, 10)
    page = request.GET.get('page')
    receipt_page = p.get_page(page)
    #return render(request, 'receipts/receipt_list.html', {'receipt_list':receipt_list})
    return render(request, 'receipts/receipt_list.html', {'receipt_page':receipt_page})

def receipt_add(request):
    if request.method == "POST":
        form = ReceiptForm(request.POST)
        if form.is_valid():
            #form.save()
            receipt = form.save(commit=False)
            receipt.account_user = request.user.id
            receipt.save()
            messages.success(request, ("Receipt Addition Successful!"))
            return redirect('receipt-list')
        else:
            messages.success(request, ("Receipt Addition Error! Please try again!"))
    else:
        form = ReceiptForm
    return render(request, 'receipts/receipt_add.html', {'form':form})

def receipt_upload(request):
    if request.method == "POST" and request.FILES['receiptFile']:
        receiptFile = request.FILES['receiptFile']
        #Size of the file 2MB = 2 * 1024 * 1024
        if receiptFile.size > 2097152:
            messages.success(request, ("Receipt file size cannot exceed 2MB!"))
            return render(request, 'receipts/receipt_upload.html', {})

        receiptFileDb = ReceiptFile()
        receiptFileDb.upload_file_name = receiptFile.name
        receiptFileDb.account_user = request.user.id
        receiptFileDb.save()
        if receiptFile.name.endswith('.jpg'):
            receiptFileDb.file_name = 'Receipt-' + str(receiptFileDb.account_user) + '-' + str(receiptFileDb.id) + '.jpg'
        if receiptFile.name.endswith('.jpeg'):
            receiptFileDb.file_name = 'Receipt-' + str(receiptFileDb.account_user) + '-' + str(receiptFileDb.id) + '.jpeg'
        if receiptFile.name.endswith('.png'):
            receiptFileDb.file_name = 'Receipt-' + str(receiptFileDb.account_user) + '-' + str(receiptFileDb.id) + '.png'
        receiptFileDb.save()

        receipt = Receipt()
        receipt.name = receiptFileDb.file_name
        receipt.date_receipt = '2021-12-08 09:00'
        receipt.vendor_name = ''
        receipt.amount_total = 0.0
        receipt.account_user = request.user.id

#        fss = FileSystemStorage()
#        receiptFileSaved = fss.save(receiptFileDb.file_name, receiptFile)
#        fileUrl = fss.url(receiptFileSaved)

        s3Reseponse = aws.s3_upload_fileobj(receiptFile, 's3-bucket-receipttracker', receipt.name)
        #print(s3Reseponse)
        
        receiptFileS3Url = aws.s3_presigned_url('s3-bucket-receipttracker', receipt.name)
        #print(receiptFileS3Url)

        form = ReceiptForm(instance=receipt)

        messages.success(request, ("Receipt file uploaded successfully"))
        return render(request, 'receipts/receipt_add.html', {'form':form, 'receiptFileS3Url':receiptFileS3Url})
		
    return render(request, 'receipts/receipt_upload.html', {})
