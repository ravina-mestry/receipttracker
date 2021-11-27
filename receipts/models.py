from django.db import models

class Receipt(models.Model):
    name = models.CharField('Name', max_length=64)
    date_receipt = models.DateTimeField('Date Receipt')
    vendor_name = models.CharField('Vendor Name', max_length=64)
    amount_total = models.FloatField('Total Amount')
    
    def __str__(self):
        return self.name
