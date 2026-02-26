"""
BrosDen-AV Mailer Utility
==========================
Central mailing logic using Django's email infrastructure (Gmail SMTP).

Usage examples:
    from mailer.services import (
        send_welcome_email,
        send_booking_confirmation,
        send_booking_status_update,
        send_payment_receipt,
        send_contract_signed,
        send_kyc_status,
        send_support_ticket_update,
        send_password_reset,
        send_custom_email,
    )
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Core Dispatcher
# ─────────────────────────────────────────────

def _send(subject: str, to: list[str], template: str, context: dict, reply_to: str = None) -> bool:
    """
    Internal helper. Renders a txt + HTML template pair and sends the email.
    Returns True on success, False on failure.

    Templates must live in: mailer/templates/mailer/emails/<template>/
        - <template>.txt   (plain text fallback)
        - <template>.html  (HTML body)
    """
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', False):
        logger.info(f"[MAILER] Email toggle disabled. Skipping mail: '{subject}' → {to}")
        return False

    try:
        txt_body  = render_to_string(f'mailer/emails/{template}.txt',  context)
        html_body = render_to_string(f'mailer/emails/{template}.html', context)

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


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def send_welcome_email(user) -> bool:
    """Send a welcome / account-created email."""
    return _send(
        subject=f"Welcome to BrosDen-AV, {user.first_name or user.username}!",
        to=[user.email],
        template='welcome',
        context={'user': user},
    )


def send_booking_confirmation(booking) -> bool:
    """Notify tenant that a booking request was received."""
    return _send(
        subject=f"Booking Request Received — {booking.property.title}",
        to=[booking.tenant.email],
        template='booking_confirmation',
        context={'booking': booking},
    )


def send_booking_status_update(booking) -> bool:
    """
    Notify the tenant when a booking status changes
    (approved / rejected / cancelled).
    """
    status_label = dict(booking.STATUS_CHOICES).get(booking.status, booking.status)
    return _send(
        subject=f"Booking {status_label} — {booking.property.title}",
        to=[booking.tenant.email],
        template='booking_status',
        context={'booking': booking, 'status_label': status_label},
    )


def send_new_booking_to_owner(booking) -> bool:
    """Notify property owner about a new incoming booking request."""
    return _send(
        subject=f"New Booking Request — {booking.property.title}",
        to=[booking.property.owner.email],
        template='new_booking_owner',
        context={'booking': booking},
    )


def send_payment_receipt(payment) -> bool:
    """Send a payment confirmation / receipt email."""
    return _send(
        subject=f"Payment Receipt #{payment.id} — BrosDen-AV",
        to=[payment.user.email],
        template='payment_receipt',
        context={'payment': payment},
    )


def send_contract_signed(contract, recipient) -> bool:
    """Notify a party (owner or tenant) that a contract has been signed."""
    return _send(
        subject=f"Contract Signed — {contract.property.title}",
        to=[recipient.email],
        template='contract_signed',
        context={'contract': contract, 'recipient': recipient},
    )


def send_kyc_status(user, status: str, remarks: str = '') -> bool:
    """
    Email user about their KYC verification result.
    status: 'APPROVED' | 'REJECTED' | 'PENDING'
    """
    return _send(
        subject=f"KYC Verification {status.title()} — BrosDen-AV",
        to=[user.email],
        template='kyc_status',
        context={'user': user, 'status': status, 'remarks': remarks},
    )


def send_support_ticket_update(ticket) -> bool:
    """Notify user about an update on their support ticket."""
    return _send(
        subject=f"Support Ticket #{ticket.id} Updated — {ticket.subject}",
        to=[ticket.user.email],
        template='ticket_update',
        context={'ticket': ticket},
    )


def send_support_ticket_reply(ticket, reply) -> bool:
    """Notify user about a new reply on their support ticket."""
    return _send(
        subject=f"New Reply on Ticket #{ticket.id} — {ticket.subject}",
        to=[ticket.user.email],
        template='ticket_reply',
        context={'ticket': ticket, 'reply': reply},
    )


def send_password_reset(user, reset_url: str) -> bool:
    """Send a password reset link email."""
    return _send(
        subject="Reset Your BrosDen-AV Password",
        to=[user.email],
        template='password_reset',
        context={'user': user, 'reset_url': reset_url},
    )


def send_chat_notification(message) -> bool:
    """Notify a user (via email) that they have a new unread chat message."""
    recipient = message.room.get_other_user(message.sender)
    if not recipient or not recipient.email:
        return False
    return _send(
        subject=f"New Message from {message.sender.username} — BrosDen-AV",
        to=[recipient.email],
        template='chat_message',
        context={'message': message, 'recipient': recipient},
    )


def send_custom_email(subject: str, to: list[str], body_html: str, body_txt: str = '') -> bool:
    """
    Send a one-off custom email without a template.
    Useful for admin-triggered announcements.
    """
    if not getattr(settings, 'ENABLE_EMAIL_NOTIFICATIONS', False):
        logger.info(f"[MAILER] Email toggle disabled. Skipping custom mail: '{subject}' → {to}")
        return False

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=body_txt or 'Please view this email in an HTML-capable client.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
        )
        email.attach_alternative(body_html, 'text/html')
        email.send(fail_silently=False)
        logger.info(f"[MAILER] Custom email sent: '{subject}' → {to}")
        return True
    except Exception as exc:
        logger.error(f"[MAILER] Custom email failed: {exc}", exc_info=True)
        return False
