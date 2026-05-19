from .models import Cart


def cart_context(request):
    """Make cart item count available in all templates."""
    cart_count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            if not request.session.session_key:
                request.session.create()
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if cart:
            cart_count = cart.total_items
    except Exception:
        pass
    return {"cart_count": cart_count}
