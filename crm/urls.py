from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Customer-facing URLs
    path('profile/', views.customer_profile, name='customer_profile'),
    path('tickets/', views.support_tickets, name='support_tickets'),
    path('ticket/<str:ticket_id>/', views.support_ticket_detail, name='support_ticket_detail'),
    path('ticket/create/', views.create_support_ticket, name='create_support_ticket'),
    path('interactions/', views.customer_interactions, name='customer_interactions'),
    path('notes/', views.customer_notes, name='customer_notes'),

    # Staff URLs
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('tickets/all/', views.staff_ticket_list, name='staff_ticket_list'),
    path('ticket/<str:ticket_id>/staff/', views.staff_ticket_detail, name='staff_ticket_detail'),
    path('customers/', views.customer_list, name='customer_list'),
]