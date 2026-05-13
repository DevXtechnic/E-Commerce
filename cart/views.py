from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from shop.models import Product


def _get_cart(request):
    """Get or create cart for current user/session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )
    return cart


def view_cart(request):
    cart = _get_cart(request)
    items = cart.items.select_related("product").all()
    context = {
        "cart": cart,
        "items": items,
    }
    return render(request, "cart/cart.html", context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_cart(request)
    quantity = int(request.POST.get("quantity", 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.total_items,
            "message": f"{product.name} added to cart!",
        })

    messages.success(request, f"{product.name} added to cart!")
    return redirect(request.META.get("HTTP_REFERER", "cart:view_cart"))


def update_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get("quantity", 1))

    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.total_items,
            "subtotal": str(cart.subtotal),
            "line_total": str(item.line_total) if quantity > 0 else "0",
        })

    return redirect("cart:view_cart")


def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = item.product.name
    item.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.total_items,
            "subtotal": str(cart.subtotal),
        })

    messages.info(request, f"{name} removed from cart.")
    return redirect("cart:view_cart")
