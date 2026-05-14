from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shop.urls")),
    path("users/", include("users.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("crm/", include("crm.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
