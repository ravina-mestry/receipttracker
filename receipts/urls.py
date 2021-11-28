from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('receipt/list', views.receipt_list, name="receipt-list"),
    path('receipt/add', views.receipt_add, name="receipt-add"),
]
