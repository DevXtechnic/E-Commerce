from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import ContactMessage, Newsletter, FAQ, SiteSettings
from orders.models import Order


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message_text = request.POST.get("message")
        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message_text
        )
        messages.success(request, "Thank you for your message! We'll get back to you soon.")
        return redirect("mystore:contact")
    return render(request, "crm/contact.html")


def faq(request):
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, "crm/faq.html", {"faqs": faqs})


def about(request):
    settings = SiteSettings.objects.first()
    return render(request, "crm/about.html", {"settings": settings})


def newsletter_subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            Newsletter.objects.get_or_create(email=email)
            messages.success(request, "Thank you for subscribing!")
    return redirect(request.META.get("HTTP_REFERER", "shop:home"))


@staff_member_required
def crm_dashboard(request):
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    total_subscribers = Newsletter.objects.filter(is_active=True).count()
    recent_orders = Order.objects.all()[:10]
    recent_messages = ContactMessage.objects.all()[:10]

    from django.db.models import Sum
    total_revenue = Order.objects.filter(
        status__in=["processing", "shipped", "delivered"]
    ).aggregate(total=Sum("total"))["total"] or 0

    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "unread_messages": unread_messages,
        "total_subscribers": total_subscribers,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
        "recent_messages": recent_messages,
    }
    return render(request, "crm/crm_dashboard.html", context)
