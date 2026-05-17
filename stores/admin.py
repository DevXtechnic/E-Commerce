from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "state", "is_active", "is_flagship", "created_at"]
    list_filter = ["is_active", "is_flagship", "city", "state"]
    search_fields = ["name", "city", "state", "address"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]
