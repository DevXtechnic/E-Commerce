from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("confirmation/<str:order_number>/", views.order_confirmation, name="order_confirmation"),
    path("history/", views.order_history, name="order_history"),
    path("<str:order_number>/", views.order_detail, name="order_detail"),
]
