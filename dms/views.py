from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import admin_required
from .models import UserDocument
from datetime import datetime

@admin_required
def admin_document_vault(request):
    """Admin view to browse and manage all user documents."""
    documents = UserDocument.objects.all().select_related('user').order_by('-created_at')
    return render(request, 'dms/admin/vault.html', {
        'documents': documents,
        'portal_base': 'sys_admin/portal_base.html'
    })

@admin_required
def approve_document(request, pk):
    """Approve a document in the vault."""
    doc = get_object_or_404(UserDocument, pk=pk)
    doc.is_verified = True
    doc.verified_at = datetime.now()
    doc.save()
    
    messages.success(request, f"Document '{doc.title}' for {doc.user.username} has been verified.")
    return redirect('dms:admin_vault')

@login_required
def my_documents(request):
    """User view to see their own uploaded documents."""
    documents = UserDocument.objects.filter(user=request.user)
    # Determine which portal base to use for the user
    portal_base = request.user.portal_base
    return render(request, 'dms/my_documents.html', {
        'documents': documents,
        'portal_base': portal_base
    })
