from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.db.models import Q
from accounts.models import User


@login_required
def chat_list(request):
    """List all conversations for the current user."""
    conversations = request.user.conversations.all().order_by('-updated_at')
    
    unread_conversations = []
    read_conversations = []
    
    for convo in conversations:
        last_msg = convo.messages.last()
        if last_msg and not last_msg.is_read and last_msg.sender != request.user:
            unread_conversations.append(convo)
        else:
            read_conversations.append(convo)
            
    return render(request, 'chat/chat_list.html', {
        'unread_conversations': unread_conversations,
        'read_conversations': read_conversations,
    })


@login_required
def chat_box(request, conversation_id):
    """Display and handle messages in a specific conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    chat_messages = conversation.messages.all()

    # Mark received messages as read
    conversation.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            # touch updated_at on the conversation
            Conversation.objects.filter(pk=conversation.pk).update(
                updated_at=__import__('django.utils.timezone', fromlist=['now']).now()
            )
            return redirect('chat:chat_box', conversation_id=conversation_id)

    return render(request, 'chat/chat_box.html', {
        'conversation': conversation,
        'chat_messages': chat_messages,
    })


@login_required
def start_conversation(request, user_id):
    """Start or retrieve a conversation with a specific user."""
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect('chat:chat_list')

    # Reuse existing conversation between the two users if one already exists
    conversation = (
        Conversation.objects
        .filter(participants=request.user)
        .filter(participants=other_user)
        .first()
    )
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)

    return redirect('chat:chat_box', conversation_id=conversation.id)
