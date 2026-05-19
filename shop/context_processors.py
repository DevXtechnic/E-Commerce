from .models import Notification


def notif_context(request):
    if not request.user.is_authenticated:
        return {"notif_count": 0}
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {"notif_count": count}
