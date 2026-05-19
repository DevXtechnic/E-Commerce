from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, Brand, Category
from .search_index import search_index


@receiver(post_save, sender=Product)
def index_product(sender, instance, **kwargs):
    if instance.is_active:
        score = 15 if instance.is_featured else 10
        cat_name = instance.category.name if instance.category else None
        search_index.add_entry(instance.name, "product", instance.get_absolute_url(), score, cat_name)
    else:
        search_index.remove_entry(instance.name, "product")


@receiver(post_delete, sender=Product)
def unindex_product(sender, instance, **kwargs):
    search_index.remove_entry(instance.name, "product")


@receiver(post_save, sender=Brand)
def index_brand(sender, instance, **kwargs):
    search_index.add_entry(instance.name, "brand", f"/products/?brand={instance.slug}", 5)


@receiver(post_delete, sender=Brand)
def unindex_brand(sender, instance, **kwargs):
    search_index.remove_entry(instance.name, "brand")


@receiver(post_save, sender=Category)
def index_category(sender, instance, **kwargs):
    search_index.add_entry(instance.name, "category", instance.get_absolute_url(), 5)


@receiver(post_delete, sender=Category)
def unindex_category(sender, instance, **kwargs):
    search_index.remove_entry(instance.name, "category")
