from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.models import Cart, StockReservation


RESERVATION_EXPIRY_MINUTES = 10


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:view_cart")

    items = cart.items.select_related("product").prefetch_related("reservations").all()

    calculated_subtotal = sum(item.product.current_price * item.quantity for item in items)
    price_changes = []
    for item in items:
        expected = item.product.current_price * item.quantity
        if abs(item.line_total - expected) > 0.01:
            price_changes.append({
                "name": item.product.name,
                "old_price": item.line_total,
                "new_price": expected,
            })

    unavailable_items = []
    for item in items:
        if item.product.available_stock < item.quantity:
            unavailable_items.append({
                "name": item.product.name,
                "requested": item.quantity,
                "available": item.product.available_stock,
            })

    if request.method == "POST":
        if unavailable_items:
            item_names = ", ".join(i["name"] for i in unavailable_items)
            messages.error(
                request,
                f"Cannot checkout: {item_names} no longer have sufficient stock. Please update your cart."
            )
            return redirect("cart:view_cart")

        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total = calculated_subtotal
                    order.save()

                    for item in items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            product_name=item.product.name,
                            quantity=item.quantity,
                            price=item.product.current_price,
                        )
                        item.product.stock -= item.quantity
                        item.product.save()

                    expiry = timezone.now() - timedelta(minutes=RESERVATION_EXPIRY_MINUTES)
                    StockReservation.objects.filter(
                        cart_item__cart=cart, reserved_at__gte=expiry
                    ).delete()

                    cart.items.all().delete()

                messages.success(request, f"Order #{order.order_number} placed successfully!")
                return redirect("orders:order_confirmation", order_number=order.order_number)
            except Exception as e:
                messages.error(request, f"Error placing order: {str(e)}")
                return redirect("cart:view_cart")
    else:
        form = CheckoutForm(user=request.user)

    context = {
        "form": form,
        "cart": cart,
        "items": items,
        "unavailable_items": unavailable_items,
        "price_changes": price_changes,
        "calculated_total": calculated_subtotal,
    }
    return render(request, "orders/checkout.html", context)


@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "orders/order_confirmation.html", {"order": order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "orders/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
