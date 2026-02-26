from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    In-app notification model. Supports categorized, per-user notifications
    that can be actioned or linked to specific parts of the app.
    """

    TYPE_CHOICES = (
        ('BOOKING',     'Booking'),
        ('PAYMENT',     'Payment'),
        ('CONTRACT',    'Contract'),
        ('CHAT',        'Chat'),
        ('SUPPORT',     'Support'),
        ('PROPERTY',    'Property'),
        ('KYC',         'KYC'),
        ('SYSTEM',      'System'),
    )

    ICON_MAP = {
        'BOOKING':   'fa-calendar-check',
        'PAYMENT':   'fa-credit-card',
        'CONTRACT':  'fa-file-signature',
        'CHAT':      'fa-comments',
        'SUPPORT':   'fa-headset',
        'PROPERTY':  'fa-city',
        'KYC':       'fa-shield-halved',
        'SYSTEM':    'fa-bell',
    }

    COLOR_MAP = {
        'BOOKING':   'blue',
        'PAYMENT':   'green',
        'CONTRACT':  'purple',
        'CHAT':      'indigo',
        'SUPPORT':   'orange',
        'PROPERTY':  'cyan',
        'KYC':       'yellow',
        'SYSTEM':    'slate',
    }

    recipient    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SYSTEM')
    title        = models.CharField(max_length=255)
    message      = models.TextField()
    link         = models.CharField(max_length=500, blank=True, null=True,
                                    help_text="Optional URL to navigate when notification is clicked.")
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.recipient.username}"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    @property
    def icon(self):
        return self.ICON_MAP.get(self.notification_type, 'fa-bell')

    @property
    def color(self):
        return self.COLOR_MAP.get(self.notification_type, 'slate')


def send_notification(recipient, title, message, notification_type='SYSTEM', link=None):
    """
    Helper to create a notification for a user.
    Import and call this from any app:
        from notifications.models import send_notification
        send_notification(user, "Booking Confirmed", "Your booking has been approved.", 'BOOKING', link='/booking/1/')
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
