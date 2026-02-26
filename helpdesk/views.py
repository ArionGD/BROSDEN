from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Ticket, TicketReply

@login_required
def support_home(request):
    """Support home showing categories and user's tickets."""
    categories = Category.objects.all()
    user_tickets = request.user.tickets.all()[:5]
    return render(request, 'helpdesk/support_home.html', {
        'categories': categories,
        'user_tickets': user_tickets
    })

@login_required
def create_ticket(request):
    """Handle ticket submission."""
    categories = Category.objects.all()
    if request.method == 'POST':
        category_id = request.POST.get('category')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'MEDIUM')
        
        category = get_object_or_404(Category, id=category_id)
        
        Ticket.objects.create(
            user=request.user,
            category=category,
            subject=subject,
            description=description,
            priority=priority
        )
        messages.success(request, "Support ticket created successfully! We will get back to you soon.")
        return redirect('helpdesk:ticket_list')
        
    return render(request, 'helpdesk/create_ticket.html', {'categories': categories})

@login_required
def ticket_list(request):
    """View all tickets submitted by the user."""
    tickets = request.user.tickets.all()
    return render(request, 'helpdesk/ticket_list.html', {'tickets': tickets})

@login_required
def ticket_detail(request, ticket_id):
    """View ticket details and replies."""
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            TicketReply.objects.create(
                ticket=ticket,
                user=request.user,
                message=message
            )
            ticket.status = 'OPEN' # Re-open if closed? Or just update timestamp
            ticket.save()
            return redirect('helpdesk:ticket_detail', ticket_id=ticket.id)
            
    return render(request, 'helpdesk/ticket_detail.html', {'ticket': ticket})
