from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.models import Cart


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:view_cart")

    items = cart.items.select_related("product").all()

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.subtotal
            order.save()

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.current_price,
                )
                # Decrease stock
                item.product.stock -= item.quantity
                item.product.save()

            # Clear the cart
            cart.items.all().delete()

            messages.success(request, f"Order #{order.order_number} placed successfully!")
            return redirect("orders:order_confirmation", order_number=order.order_number)
    else:
        form = CheckoutForm(user=request.user)

    context = {
        "form": form,
        "cart": cart,
        "items": items,
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
