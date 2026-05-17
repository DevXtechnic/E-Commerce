from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from django.utils import timezone
from datetime import timedelta


RESERVATION_EXPIRY_MINUTES = 15


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="carts"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart - {self.user.username}"
        return f"Cart - Session {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["cart", "product"]

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def line_total(self):
        return self.product.current_price * self.quantity

    @property
    def reserved_quantity(self):
        now = timezone.now()
        expiry = now - timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
        return sum(
            r.quantity for r in self.reservations.filter(reserved_at__gte=expiry)
        )

    @property
    def is_available(self):
        return self.product.available_stock >= self.quantity

    @property
    def remaining_stock(self):
        return self.product.available_stock


class StockReservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reservations")
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name="reservations")
    quantity = models.PositiveIntegerField()
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["product", "expires_at"]),
        ]

    def __str__(self):
        return f"{self.product.name} x{self.quantity} (expires {self.expires_at})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def cleanup_expired(cls):
        """Delete all expired reservations and return count."""
        expired = cls.objects.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        return count
