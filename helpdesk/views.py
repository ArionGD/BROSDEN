from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Ticket, TicketReply


@login_required
def support_home(request):
    """Support home showing categories and user's recent tickets."""
    categories = Category.objects.all()
    user_tickets = request.user.tickets.all()[:5]
    return render(request, 'helpdesk/support_home.html', {
        'categories': categories,
        'user_tickets': user_tickets,
    })


@login_required
def create_ticket(request):
    """Handle ticket submission form."""
    categories = Category.objects.all()
    if request.method == 'POST':
        category_id = request.POST.get('category')
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'MEDIUM')

        if subject and description:
            category = get_object_or_404(Category, id=category_id)
            Ticket.objects.create(
                user=request.user,
                category=category,
                subject=subject,
                description=description,
                priority=priority,
            )
            messages.success(request, "Support ticket created! We'll get back to you soon.")
            return redirect('helpdesk:ticket_list')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'helpdesk/create_ticket.html', {'categories': categories})


@login_required
def ticket_list(request):
    """View all tickets submitted by the current user."""
    tickets = request.user.tickets.all()
    return render(request, 'helpdesk/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_detail(request, ticket_id):
    """View ticket details and add replies."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        reply_text = request.POST.get('message', '').strip()
        if reply_text:
            TicketReply.objects.create(ticket=ticket, user=request.user, message=reply_text)
            # Re-open if closed so staff can respond again
            if ticket.status == 'CLOSED':
                ticket.status = 'OPEN'
                ticket.save()
            return redirect('helpdesk:ticket_detail', ticket_id=ticket.id)

    return render(request, 'helpdesk/ticket_detail.html', {'ticket': ticket})
