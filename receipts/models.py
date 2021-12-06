from django.db import models

class Receipt(models.Model):
    name = models.CharField('Name', max_length=64)
    date_receipt = models.DateTimeField('Date Receipt')
    vendor_name = models.CharField('Vendor Name', max_length=64)
    amount_total = models.FloatField('Total Amount')
    account_user = models.IntegerField("Account User", blank=False)

    def __str__(self):
        return self.name

class ReceiptFile(models.Model):
    upload_file_name = models.CharField('Upload File Name', max_length=64)
    account_user = models.IntegerField("Account User", blank=False)
    file_name = models.CharField('File Name', max_length=64)
