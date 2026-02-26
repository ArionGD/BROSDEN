from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Notification

# Shared read-status filter choices for the template
_READ_CHOICES = [
    ('ALL',    'All',    'bg-slate-800'),
    ('UNREAD', 'Unread', 'bg-amber-500'),
    ('READ',   'Read',   'bg-green-500'),
]


@login_required
def notification_list(request):
    """Main in-app notification page — works for both Owner and Tenant."""
    qs = Notification.objects.filter(recipient=request.user)

    filter_type = request.GET.get('type', 'ALL')
    if filter_type != 'ALL':
        qs = qs.filter(notification_type=filter_type)

    read_filter = request.GET.get('read', 'ALL')
    if read_filter == 'UNREAD':
        qs = qs.filter(is_read=False)
    elif read_filter == 'READ':
        qs = qs.filter(is_read=True)

    page_obj = Paginator(qs, 15).get_page(request.GET.get('page'))
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        'page_obj':      page_obj,
        'unread_count':  unread_count,
        'filter_type':   filter_type,
        'read_filter':   read_filter,
        'type_choices':  Notification.TYPE_CHOICES,
        'read_choices':  _READ_CHOICES,
    }

    template = 'notifications/owner_notifications.html' if request.user.is_owner else 'notifications/tenant_notifications.html'
    return render(request, template, context)


@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_read()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'status': 'ok', 'unread_count': count})
    return redirect('notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'unread_count': 0})
    return redirect('notifications:list')


@login_required
@require_POST
def delete_notification(request, pk):
    get_object_or_404(Notification, pk=pk, recipient=request.user).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'deleted'})
    return redirect('notifications:list')


@login_required
def unread_count_api(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})
