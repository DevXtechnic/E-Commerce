from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('ne', 'Nepali'),
    ])
    newsletter_subscribed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate a simple ticket ID: TKT-YYYYMMDD-XXXX
            today = timezone.now().strftime('%Y%m%d')
            # We'll use a simple random suffix for now; in production, use a better method
            import random
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            self.ticket_id = f'TKT-{today}-{suffix}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.ticket_id}: {self.subject}"


class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_staff_response = models.BooleanField(default=False)  # True if replied by staff, False if by customer
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.ticket.ticket_id} by {self.author.username}"


class CustomerInteraction(models.Model):
    INTERACTION_TYPES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('chat', 'Live Chat'),
        ('other', 'Other'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)
    subject = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    interacted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='made_interactions')
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)  # For calls/meetings
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.interaction_type} with {self.customer.username} on {self.created_at.strftime('%Y-%m-%d')}"


class CustomerNote(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_notes')
    note = models.TextField()
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.customer.username} by {self.author.username}"