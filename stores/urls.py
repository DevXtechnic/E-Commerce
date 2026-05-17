from django.urls import path
from . import views

app_name = "stores"

urlpatterns = [
    path("", views.StoreListView.as_view(), name="store_list"),
    path("<slug:slug>/", views.StoreDetailView.as_view(), name="store_detail"),
]
