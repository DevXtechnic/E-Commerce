from django.db import models
from django.contrib.auth.models import User
from shop.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
        ("bank", "Bank Transfer"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default="cod"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = "DXT-" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        super().save(*args, **kwargs)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=300)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def line_total(self):
        return self.price * self.quantity
