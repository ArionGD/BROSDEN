"""
BrosDen-AV Mailer Utility
==========================
Central mailing logic using Django's email infrastructure (Gmail SMTP).

We only send emails for:
1. Registration (Welcome & Credentials)
2. Booking Approval Confirmation
3. Contract Creation (Post payment)
All other notifications should use the in-app notification system.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def _send(subject: str, to: list[str], template: str, context: dict, reply_to: str = None) -> bool:
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', False):
        logger.info(f"[MAILER] Email toggle disabled. Skipping mail: '{subject}' → {to}")
        return False

    try:
        html_body = render_to_string(f'mailer/emails/{template}.html', context)
        # Fallback text if needed, here just using stripped tags or simple string
        txt_body = "Please view this email in an HTML-capable client." 

        email = EmailMultiAlternatives(
            subject=subject,
            body=txt_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
            reply_to=[reply_to] if reply_to else None,
        )
        email.attach_alternative(html_body, 'text/html')
        email.send(fail_silently=False)
        logger.info(f"[MAILER] Email sent: '{subject}' → {to}")
        return True

    except Exception as exc:
        logger.error(f"[MAILER] Failed to send '{subject}' → {to}: {exc}", exc_info=True)
        return False


# 1. Registration Email
def send_welcome_email(user, password, request=None) -> bool:
    """Send a welcome email with credentials and a link to the website."""
    
    website_link = request.build_absolute_uri('/') if request else 'http://127.0.0.1:8000/'
    login_link = request.build_absolute_uri(reverse('accounts:login')) if request else 'http://127.0.0.1:8000/accounts/login/'

    return _send(
        subject=f"Welcome to BrosDen-AV, {user.first_name or user.username}!",
        to=[user.email],
        template='welcome',
        context={
            'user': user, 
            'password': password, 
            'website_link': website_link,
            'login_link': login_link
        },
    )

# 2. Booking Approved
def send_booking_approved_email(booking, request=None) -> bool:
    """Notify the tenant when a booking is approved by the owner."""
    website_link = request.build_absolute_uri('/') if request else 'http://127.0.0.1:8000/'
    return _send(
        subject=f"Booking Approved! — {booking.property.title}",
        to=[booking.tenant.email],
        template='booking_status',
        context={'booking': booking, 'status_label': 'Approved', 'website_link': website_link},
    )

# 3. Contract Created
def send_contract_created_email(contract, recipient, request=None) -> bool:
    """Notify that a contract has been created/signed after payment."""
    website_link = request.build_absolute_uri('/') if request else 'http://127.0.0.1:8000/'
    return _send(
        subject=f"Contract Created — {contract.property.title}",
        to=[recipient.email],
        template='contract_signed',
        context={'contract': contract, 'recipient': recipient, 'website_link': website_link},
    )
