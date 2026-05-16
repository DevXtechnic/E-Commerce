from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("products/<slug:slug>/review/", views.add_review, name="add_review"),
    path("search/", views.search, name="search"),
]
