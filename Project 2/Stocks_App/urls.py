from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('Add_Transaction/', views.Add_Transaction, name="Add_Transaction"),
    path('Buy_Stocks/', views.Buy_Stocks, name="Buy_Stocks"),
    path('Query_results/', views.Query_results, name="Query_results"),
    ]