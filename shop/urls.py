from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("products/<slug:slug>/review/", views.add_review, name="add_review"),
    path("search/", views.search, name="search"),
    path("suggestions/", views.suggestions, name="suggestions"),
    path("notifications/", views.notifications_page, name="notifications"),
    path("notifications/unread-count/", views.unread_count, name="unread_count"),
    path("notifications/new/", views.new_toasts, name="new_toasts"),
    path("notifications/mark-read/<int:notif_id>/", views.mark_read, name="mark_read"),
    path("notifications/mark-all-read/", views.mark_all_read, name="mark_all_read"),
]
