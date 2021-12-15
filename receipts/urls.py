from django.urls import path
from . import views

# define home and receipt list, add and upload urls and views
urlpatterns = [
    path('', views.home, name="home"),
    path('receipt/list', views.receipt_list, name="receipt-list"),
    path('receipt/add', views.receipt_add, name="receipt-add"),
    path('receipt/upload', views.receipt_upload, name="receipt-upload"),
]
