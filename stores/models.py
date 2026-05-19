from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly identifier")
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="USA")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="stores/", blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    opening_hours = models.TextField(
        help_text="e.g., Mon-Fri: 9AM-8PM, Sat: 10AM-6PM, Sun: Closed"
    )
    is_active = models.BooleanField(default=True)
    is_flagship = models.BooleanField(default=False, help_text="Main store location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Stores"

    def __str__(self):
        return self.name

    def get_full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
