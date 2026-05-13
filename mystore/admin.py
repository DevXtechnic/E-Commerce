from django.contrib import admin
from .models import ContactMessage, Newsletter, FAQ, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "name", "email", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    list_editable = ["is_read"]
    search_fields = ["subject", "name", "email"]


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ["email", "subscribed_at", "is_active"]
    list_filter = ["is_active"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["site_name", "tagline"]
