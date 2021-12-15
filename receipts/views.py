import datetime
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Receipt, ReceiptFile
from .forms import ReceiptForm
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from aws_rekognition_parser_pkg import aws_rekognition_parser
from django.db.models import Sum, Max, Avg
from . import aws

# home function retrurns the home.html template
# if logged in, it generates the stats data for all receipts and receipts last month to be displayed
def home(request):
    if request.user.id != None:
        
        vendor_name_distinct_count = 0
        receipt_amount_total = 0.0
        receipt_amount_max = 0.0
        receipt_amount_avg = 0.0
    
        vendor_name_distinct_count_lm = 0
        receipt_amount_total_lm = 0.0
        receipt_amount_max_lm = 0.0
        receipt_amount_avg_lm = 0.0

        receipt_list = Receipt.objects.filter(account_user=request.user.id).all()
        receipt_count = receipt_list.count()
        if receipt_count > 0:
            vendor_name_distinct_count = receipt_list.values('vendor_name').distinct().count()
            receipt_amount_total = round(receipt_list.aggregate(Sum('amount_total'))['amount_total__sum'], 2)
            receipt_amount_max = round(receipt_list.aggregate(Max('amount_total'))['amount_total__max'], 2)
            receipt_amount_avg = round(receipt_list.aggregate(Avg('amount_total'))['amount_total__avg'], 2)
    
        receipt_list_lm = Receipt.objects.filter(account_user=request.user.id).filter(date_receipt__range=['2021-11-01', '2021-11-30']).all()
        receipt_count_lm = receipt_list_lm.count()
        if receipt_count_lm > 0:
            vendor_name_distinct_count_lm = receipt_list_lm.values('vendor_name').distinct().count()
            receipt_amount_total_lm = round(receipt_list_lm.aggregate(Sum('amount_total'))['amount_total__sum'], 2)
            receipt_amount_max_lm = round(receipt_list_lm.aggregate(Max('amount_total'))['amount_total__max'], 2)
            receipt_amount_avg_lm = round(receipt_list_lm.aggregate(Avg('amount_total'))['amount_total__avg'], 2)

        return render(request, 'receipts/home.html', {'receipt_count':receipt_count, 'vendor_name_distinct_count':vendor_name_distinct_count, 'receipt_amount_total':receipt_amount_total, 'receipt_amount_max':receipt_amount_max, 'receipt_amount_avg':receipt_amount_avg, 'receipt_count_lm':receipt_count_lm, 'vendor_name_distinct_count_lm':vendor_name_distinct_count_lm, 'receipt_amount_total_lm':receipt_amount_total_lm, 'receipt_amount_max_lm':receipt_amount_max_lm, 'receipt_amount_avg_lm':receipt_amount_avg_lm})
    else:
        return render(request, 'receipts/home.html', {})

# receipt_list function returns the list of receipts for the logged in user ordered descending by id (order of upload upload)
# it uses django paginator to return the pages to receipt_list.html template
def receipt_list(request):
    receipt_list = Receipt.objects.all().filter(account_user=request.user.id).order_by('-id')
    p = Paginator(receipt_list, 10)
    page = request.GET.get('page')
    receipt_page = p.get_page(page)
    #return render(request, 'receipts/receipt_list.html', {'receipt_list':receipt_list})
    return render(request, 'receipts/receipt_list.html', {'receipt_page':receipt_page})

# receipt_add function returns the receipt_add template with ReceiptForm if it is a GET request
# if the request is POST and then form is valid then it saves the form without commiting, adds the logged in user to receipt and then saves the form in database. 
#   Then returns receipt add success message and redirects to receipt list to view it.
# if the request is POST and then form is not valid then it returns form addition error and renders the receipt_add template to show the error message.
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

# receipt_upload function returns the receipt_upload template if it is a GET request
# if request method is POST and requestFile upload is present then it will carry out below steps
#   Restrict the upload file size to 2MB and return error if it is > 2MB
#   Save receiptFile in database with file name in format Receipt-<account user id>-<receiptFile id>.<file extension>
#   Upload receiptFile in s3 bucket
#   Use AWS Rekognition service to read text in file and save the rekognitionResponse in json format on s3 bucket.
#   Use parse_rekognition_response_receipt_text function (from custom python library aws_rekognition_parser) to detect the vendor name and total amount from the text.
#   Build the receipt model from above steps (by reading info from uploaded file) and get instance of ReceiptForm
#   Generate presigned url for uploaded receiptFile in s3 bucket
#   Return receipt upload success message and redirect to receipt add template with ReceiptForm and presigned url to display the results to the user and ask him to add the receipt.
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
        receipt.date_receipt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        receipt.vendor_name = ''
        receipt.amount_total = 0.0
        receipt.account_user = request.user.id

#        fss = FileSystemStorage()
#        receiptFileSaved = fss.save(receiptFileDb.file_name, receiptFile)
#        fileUrl = fss.url(receiptFileSaved)

        s3Reseponse = aws.s3_upload_fileobj(receiptFile, 's3-bucket-receipttracker', receipt.name)
        #print(s3Reseponse)
        
        rekognitionResponse = aws.rekognition_detect_text('s3-bucket-receipttracker', receipt.name)
        #print(rekognitionResponse)
        
        vendorNameList = ['Tesco', 'Dunnes', 'Lidl', 'Aldi', 'SuperValu', 'Spar', 'Centra', 'Mace']
        receiptText = aws_rekognition_parser.parse_rekognition_response_receipt_text(rekognitionResponse, vendorNameList)
        #receiptText = aws.parse_rekognition_response_receipt_text(rekognitionResponse, vendorNameList)
        
        receipt.vendor_name = receiptText['vendorName']
        receipt.amount_total = receiptText['amountTotal']

        form = ReceiptForm(instance=receipt)

        receiptFileS3Url = aws.s3_presigned_url('s3-bucket-receipttracker', receipt.name)
        #print(receiptFileS3Url)

        messages.success(request, ("Receipt file uploaded successfully"))
        return render(request, 'receipts/receipt_add.html', {'form':form, 'receiptFileS3Url':receiptFileS3Url})
		
    return render(request, 'receipts/receipt_upload.html', {})
