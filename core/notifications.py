import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

def send_simulated_whatsapp(request, phone, message):
    """
    Mocks sending a WhatsApp/SMS notification.
    In a production app, this would call Twilio or a similar API.
    For the college demo, we use Django messages to show the notification to the user.
    """
    whatsapp_icon = "https://cdn-icons-png.flaticon.com/512/733/733585.png"
    
    # We use a custom level or just format the message to look like a WhatsApp notification
    formatted_message = f"📱 WhatsApp to {phone}: {message}"
    
    # Add to django messages so it appears on the next page load
    messages.info(request, formatted_message)
    
    # Log it for audit/debugging
    logger.info(f"SIMULATED WHATSAPP: To={phone}, Msg={message}")

def notify_application_received(request, booking):
    msg = f"Hello {booking.tenant.username}, your application for {booking.property.title} was received! App ID: #DEN{booking.id}. Track it in your portal."
    send_simulated_whatsapp(request, "Registered Phone", msg)

def notify_payment_due(request, schedule):
    msg = f"Reminder: Your rent of ₹{schedule.amount} for {schedule.due_date|date:'F'} is due soon for {schedule.contract.booking.property.title}."
    send_simulated_whatsapp(request, "Registered Phone", msg)
