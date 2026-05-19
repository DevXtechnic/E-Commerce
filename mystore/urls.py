from django.urls import path
from . import views

app_name = "mystore"

urlpatterns = [
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("about/", views.about, name="about"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("dashboard/", views.crm_dashboard, name="crm_dashboard"),
]
