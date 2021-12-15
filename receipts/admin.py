from django.contrib import admin
from .models import Receipt, ReceiptFile

# register Receipt and ReceiptFile models to django admin
admin.site.register(Receipt)
admin.site.register(ReceiptFile)
