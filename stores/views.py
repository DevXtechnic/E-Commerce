from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Store


class StoreListView(ListView):
    model = Store
    template_name = "stores/store_list.html"
    context_object_name = "stores"

    def get_queryset(self):
        return Store.objects.filter(is_active=True)


class StoreDetailView(DetailView):
    model = Store
    template_name = "stores/store_detail.html"
    context_object_name = "store"

    def get_queryset(self):
        return Store.objects.filter(is_active=True)
