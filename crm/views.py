from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from .models import CustomerProfile, SupportTicket, TicketResponse, CustomerInteraction, CustomerNote
from django.contrib.auth.models import User


def is_staff_or_admin(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


@login_required
def customer_profile(request):
    """Display and edit customer profile"""
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Handle profile update
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.province = request.POST.get('province', '')
        profile.postal_code = request.POST.get('postal_code', '')
        profile.preferred_language = request.POST.get('preferred_language', 'en')
        profile.newsletter_subscribed = 'newsletter_subscribed' in request.POST

        # Handle date of birth
        dob = request.POST.get('date_of_birth')
        if dob:
            profile.date_of_birth = dob
        else:
            profile.date_of_birth = None

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('crm:customer_profile')

    context = {
        'profile': profile,
    }
    return render(request, 'crm/customer_profile.html', context)


@login_required
def support_tickets(request):
    """List customer's support tickets"""
    tickets = SupportTicket.objects.filter(customer=request.user).order_by('-created_at')

    context = {
        'tickets': tickets,
    }
    return render(request, 'crm/support_tickets.html', context)


@login_required
def support_ticket_detail(request, ticket_id):
    """Display a specific support ticket and handle responses"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id, customer=request.user)
    responses = ticket.responses.all().order_by('created_at')

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            TicketResponse.objects.create(
                ticket=ticket,
                author=request.user,
                message=message,
                is_staff_response=False
            )
            messages.success(request, 'Response added successfully!')
            return redirect('crm:support_ticket_detail', ticket_id=ticket_id)

    context = {
        'ticket': ticket,
        'responses': responses,
    }
    return render(request, 'crm/support_ticket_detail.html', context)


@login_required
def create_support_ticket(request):
    """Create a new support ticket"""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'medium')

        if subject and description:
            ticket = SupportTicket.objects.create(
                customer=request.user,
                subject=subject,
                description=description,
                priority=priority
            )
            messages.success(request, f'Support ticket {ticket.ticket_id} created successfully!')
            return redirect('crm:support_ticket_detail', ticket_id=ticket.ticket_id)
        else:
            messages.error(request, 'Please fill in both subject and description.')

    context = {
        'priority_choices': SupportTicket.PRIORITY_CHOICES,
    }
    return render(request, 'crm/create_support_ticket.html', context)


@login_required
def customer_interactions(request):
    """List customer's interactions"""
    interactions = CustomerInteraction.objects.filter(customer=request.user).order_by('-created_at')

    context = {
        'interactions': interactions,
    }
    return render(request, 'crm/customer_interactions.html', context)


@login_required
def customer_notes(request):
    """List notes for the customer (only visible to the customer)"""
    notes = CustomerNote.objects.filter(customer=request.user).order_by('-created_at')

    context = {
        'notes': notes,
    }
    return render(request, 'crm/customer_notes.html', context)


# Staff views
@login_required
@user_passes_test(is_staff_or_admin)
def staff_dashboard(request):
    """Staff CRM dashboard"""
    # Stats
    total_customers = User.objects.filter(customer_profile__isnull=False).count()
    open_tickets = SupportTicket.objects.filter(status__in=['open', 'in_progress']).count()
    resolved_today = SupportTicket.objects.filter(
        status='resolved',
        resolved_at__date=timezone.now().date()
    ).count()

    recent_tickets = SupportTicket.objects.select_related('customer').order_by('-created_at')[:10]

    context = {
        'total_customers': total_customers,
        'open_tickets': open_tickets,
        'resolved_today': resolved_today,
        'recent_tickets': recent_tickets,
    }
    return render(request, 'crm/staff_dashboard.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def staff_ticket_list(request):
    """Staff view of all tickets"""
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')

    tickets = SupportTicket.objects.select_related('customer').all()

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    tickets = tickets.order_by('-created_at')

    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': SupportTicket.STATUS_CHOICES,
        'priority_choices': SupportTicket.PRIORITY_CHOICES,
    }
    return render(request, 'crm/staff_ticket_list.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def staff_ticket_detail(request, ticket_id):
    """Staff view/detail of a ticket with ability to respond and update status"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    responses = ticket.responses.all().order_by('created_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_response':
            message = request.POST.get('message', '').strip()
            if message:
                TicketResponse.objects.create(
                    ticket=ticket,
                    author=request.user,
                    message=message,
                    is_staff_response=True
                )
                messages.success(request, 'Response added successfully!')

        elif action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(SupportTicket.STATUS_CHOICES):
                ticket.status = new_status
                if new_status == 'resolved' and not ticket.resolved_at:
                    ticket.resolved_at = timezone.now()
                elif new_status != 'resolved':
                    ticket.resolved_at = None
                ticket.save()
                messages.success(request, 'Ticket status updated successfully!')

        return redirect('crm:staff_ticket_detail', ticket_id=ticket_id)

    context = {
        'ticket': ticket,
        'responses': responses,
        'status_choices': SupportTicket.STATUS_CHOICES,
    }
    return render(request, 'crm/staff_ticket_detail.html', context)


@login_required
@user_passes_test(is_staff_or_admin)
def customer_list(request):
    """Staff view of all customers"""
    search_query = request.GET.get('q', '')

    customers = User.objects.filter(customer_profile__isnull=False).select_related('customer_profile')

    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(customer_profile__phone_number__icontains=search_query) |
            Q(customer_profile__city__icontains=search_query)
        )

    customers = customers.order_by('-customer_profile__created_at')

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'crm/customer_list.html', context)