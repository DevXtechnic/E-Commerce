from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.product_list, name='product_list'),
    path('', views.product_detail, name='product_detail'),
    path('', views.cart, name='cart'),
    path('', views.checkout, name='chekout'),
    path('', views.login, name='login'),

] 