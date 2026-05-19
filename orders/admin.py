from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "quantity", "price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number", "user", "full_name", "total",
        "status", "payment_method", "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["order_number", "full_name", "email"]
    list_editable = ["status"]
    readonly_fields = ["order_number", "created_at"]
    inlines = [OrderItemInline]
