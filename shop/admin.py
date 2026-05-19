from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Review, Notification


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "order"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "brand", "price", "discount_price", "stock", "is_featured", "is_active"]
    list_filter = ["category", "brand", "is_featured", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]
    list_editable = ["price", "discount_price", "stock", "is_featured", "is_active"]
    inlines = [ProductImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "rating", "created_at"]
    list_filter = ["rating"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "type", "user", "is_read", "toast_shown", "created_at"]
    list_filter = ["type", "is_read", "toast_shown"]
    search_fields = ["title", "message"]
    readonly_fields = ["created_at"]
