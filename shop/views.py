from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg
from .models import Product, Category, Brand, Review
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    latest_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.filter(parent=None)[:6]
    deal_products = Product.objects.filter(
        is_active=True, discount_price__isnull=False
    )[:4]
    context = {
        "featured_products": featured_products,
        "latest_products": latest_products,
        "categories": categories,
        "deal_products": deal_products,
    }
    return render(request, "shop/home.html", context)


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(parent=None)
    brands = Brand.objects.all()

    category_slug = request.GET.get("category")
    brand_slug = request.GET.get("brand")
    sort = request.GET.get("sort", "newest")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(
            Q(category=active_category) | Q(category__parent=active_category)
        )

    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if sort == "price_low":
        products = products.order_by("price")
    elif sort == "price_high":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("-created_at")

    context = {
        "products": products,
        "categories": categories,
        "brands": brands,
        "active_category": active_category,
        "current_sort": sort,
    }
    return render(request, "shop/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    reviews = product.reviews.all()

    context = {
        "product": product,
        "related_products": related_products,
        "reviews": reviews,
        "specs": product.get_specs_list(),
    }
    return render(request, "shop/product_detail.html", context)


def search(request):
    query = request.GET.get("q", "")
    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__name__icontains=query)
            | Q(category__name__icontains=query)
        )

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "shop/search.html", context)


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "")
        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={"rating": rating, "comment": comment},
        )
    from django.shortcuts import redirect
    return redirect("shop:product_detail", slug=slug)
