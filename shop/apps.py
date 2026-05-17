from django.apps import AppConfig


class ShopConfig(AppConfig):
    name = "shop"

    def ready(self):
        from . import signals  # noqa
        import sys
        if any(cmd in sys.argv for cmd in ["makemigrations", "migrate", "check"]):
            return
        from .search_index import search_index
        search_index.build()
