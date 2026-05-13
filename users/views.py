from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileForm, AddressForm
from .models import Address
from shop.models import Product


def register(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to DevXtechnic! Your account has been created.")
            return redirect("shop:home")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Merge anonymous cart with user cart
            from cart.models import Cart
            session_key = request.session.session_key
            login(request, user)
            if session_key:
                anon_cart = Cart.objects.filter(session_key=session_key).first()
                user_cart = Cart.objects.filter(user=user).first()
                if anon_cart and user_cart:
                    for item in anon_cart.items.all():
                        existing = user_cart.items.filter(product=item.product).first()
                        if existing:
                            existing.quantity += item.quantity
                            existing.save()
                        else:
                            item.cart = user_cart
                            item.save()
                    anon_cart.delete()
                elif anon_cart:
                    anon_cart.user = user
                    anon_cart.save()
            messages.success(request, "Welcome back!")
            next_url = request.GET.get("next", "shop:home")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("shop:home")


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user.profile, user=request.user)

    addresses = Address.objects.filter(user=request.user)
    return render(request, "users/profile.html", {"form": form, "addresses": addresses})


@login_required
def dashboard(request):
    orders = request.user.orders.all()[:5]
    wishlist_items = []
    if hasattr(request.user, "wishlist"):
        wishlist_items = request.user.wishlist.products.all()[:4]
    context = {
        "orders": orders,
        "wishlist_items": wishlist_items,
    }
    return render(request, "users/dashboard.html", context)


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = request.user.wishlist
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.info(request, f"{product.name} removed from wishlist.")
    else:
        wishlist.products.add(product)
        messages.success(request, f"{product.name} added to wishlist!")
    return redirect(request.META.get("HTTP_REFERER", "shop:home"))


@login_required
def wishlist_view(request):
    items = request.user.wishlist.products.all()
    return render(request, "users/wishlist.html", {"items": items})


@login_required
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect("users:profile")
    else:
        form = AddressForm()
    return render(request, "users/add_address.html", {"form": form})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.info(request, "Address deleted.")
    return redirect("users:profile")
