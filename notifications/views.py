from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Notification


@login_required
def notification_list(request):
    """Main in-app notification page — works for both Owner and Tenant."""
    all_notifications = Notification.objects.filter(recipient=request.user)

    # Filter by type
    filter_type = request.GET.get('type', 'ALL')
    if filter_type != 'ALL':
        all_notifications = all_notifications.filter(notification_type=filter_type)

    # Filter by read/unread
    read_filter = request.GET.get('read', 'ALL')
    if read_filter == 'UNREAD':
        all_notifications = all_notifications.filter(is_read=False)
    elif read_filter == 'READ':
        all_notifications = all_notifications.filter(is_read=True)

    paginator = Paginator(all_notifications, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    # Type choices for filter UI
    type_choices = Notification.TYPE_CHOICES

    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
        'filter_type': filter_type,
        'read_filter': read_filter,
        'type_choices': type_choices,
    }

    # Render role-specific template
    if request.user.is_owner:
        return render(request, 'notifications/owner_notifications.html', context)
    else:
        return render(request, 'notifications/tenant_notifications.html', context)


@login_required
@require_POST
def mark_read(request, pk):
    """Mark a single notification as read via POST."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_read()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'unread_count': Notification.objects.filter(
            recipient=request.user, is_read=False).count()})
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'unread_count': 0})
    return redirect('notifications:list')


@login_required
@require_POST
def delete_notification(request, pk):
    """Delete a single notification."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'deleted'})
    return redirect('notifications:list')


@login_required
def unread_count_api(request):
    """Lightweight API endpoint — returns unread count as JSON (for header badge polling)."""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})
