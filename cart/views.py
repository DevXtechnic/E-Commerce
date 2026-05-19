from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Cart, CartItem, StockReservation
from shop.models import Product


RESERVATION_EXPIRY_MINUTES = 10


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


def _cleanup_expired_reservations():
    """Remove expired reservations and return count."""
    expired = StockReservation.objects.filter(expires_at__lt=timezone.now())
    count = expired.count()
    expired.delete()
    return count


def _create_reservation(cart_item, quantity):
    """Create a stock reservation for a cart item."""
    StockReservation.objects.create(
        product=cart_item.product,
        cart_item=cart_item,
        quantity=quantity,
    )


def _update_reservation(cart_item, new_quantity):
    """Update reservation quantity for a cart item."""
    expiry = timezone.now() - timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
    reservations = cart_item.reservations.filter(reserved_at__gte=expiry)
    current_reserved = sum(r.quantity for r in reservations)

    if new_quantity > current_reserved:
        StockReservation.objects.create(
            product=cart_item.product,
            cart_item=cart_item,
            quantity=new_quantity - current_reserved,
        )
    elif new_quantity < current_reserved:
        to_release = current_reserved - new_quantity
        for res in reservations:
            if to_release <= 0:
                break
            if res.quantity <= to_release:
                to_release -= res.quantity
                res.delete()
            else:
                res.quantity -= to_release
                res.save()
                to_release = 0


def _release_reservation(cart_item):
    """Release all active reservations for a cart item."""
    expiry = timezone.now() - timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
    cart_item.reservations.filter(reserved_at__gte=expiry).delete()


def view_cart(request):
    _cleanup_expired_reservations()
    cart = _get_cart(request)
    items = cart.items.select_related("product").prefetch_related("reservations").all()

    removed_count = 0
    expiry = timezone.now() - timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
    for item in list(items):
        active_res = item.reservations.filter(reserved_at__gte=expiry)
        if not active_res.exists():
            item.delete()
            removed_count += 1

    items = cart.items.select_related("product").prefetch_related("reservations").all()

    unavailable_items = []
    reservation_timers = {}
    for item in items:
        if item.product.available_stock < item.quantity:
            unavailable_items.append(item.id)
        active_res = item.reservations.filter(reserved_at__gte=expiry).order_by('-reserved_at').first()
        if active_res:
            remaining = (active_res.expires_at - timezone.now()).total_seconds()
            if remaining > 0:
                reservation_timers[item.id] = {
                    'seconds': int(remaining),
                    'is_urgent': remaining < 300,
                }

    if removed_count > 0:
        messages.warning(request, f"{removed_count} item(s) removed from cart — reservation expired.")

    context = {
        "cart": cart,
        "items": items,
        "unavailable_items": unavailable_items,
        "reservation_timers": reservation_timers,
    }
    return render(request, "cart/cart.html", context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_cart(request)
    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1:
        quantity = 1

    existing_item = CartItem.objects.filter(cart=cart, product=product).first()
    current_qty = existing_item.quantity if existing_item else 0
    total_requested = current_qty + quantity

    if product.available_stock < total_requested:
        available = product.available_stock - current_qty
        if available <= 0:
            error_msg = f"Sorry, {product.name} is out of stock."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": error_msg, "available": 0}, status=400)
            messages.error(request, error_msg)
            return redirect(request.META.get("HTTP_REFERER", "shop:product_list"))
        else:
            error_msg = f"Only {available} more of {product.name} available. Added {available} instead."
            quantity = available
            total_requested = current_qty + quantity

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    _update_reservation(cart_item, cart_item.quantity)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.total_items,
            "message": f"{product.name} added to cart!",
        })

    messages.success(request, f"{product.name} added to cart!")
    if request.POST.get("buy_now"):
        return redirect("orders:checkout")
    return redirect(request.META.get("HTTP_REFERER", "cart:view_cart"))


def update_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        _release_reservation(item)
        item.delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "cart_count": cart.total_items,
                "subtotal": str(cart.subtotal),
                "removed": True,
            })
        return redirect("cart:view_cart")

    if quantity > item.product.available_stock:
        quantity = item.product.available_stock
        if quantity <= 0:
            _release_reservation(item)
            item.delete()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": False,
                    "message": f"{item.product.name} is now out of stock and has been removed.",
                    "removed": True,
                }, status=400)
            messages.error(request, f"{item.product.name} is out of stock and has been removed.")
            return redirect("cart:view_cart")

    item.quantity = quantity
    item.save()
    _update_reservation(item, quantity)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.total_items,
            "subtotal": str(cart.subtotal),
            "line_total": str(item.line_total),
        })

    return redirect("cart:view_cart")


def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = item.product.name
    _release_reservation(item)
    item.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart.total_items,
            "subtotal": str(cart.subtotal),
        })

    messages.info(request, f"{name} removed from cart.")
    return redirect("cart:view_cart")


def check_stock(request):
    """AJAX endpoint to check stock availability for cart items."""
    cart = _get_cart(request)
    items = cart.items.select_related("product").prefetch_related("reservations").all()

    changes = []
    removed_ids = []

    for item in items:
        available = item.product.available_stock
        if available < item.quantity:
            changes.append({
                "item_id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "requested": item.quantity,
                "available": available,
                "is_available": available > 0,
            })
            if available <= 0:
                _release_reservation(item)
                item.delete()
                removed_ids.append(item.id)

    return JsonResponse({
        "success": True,
        "changes": changes,
        "removed_ids": removed_ids,
        "cart_count": cart.total_items,
        "subtotal": str(cart.subtotal),
    })
