from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FeedbackRequest, MonthlyFeedback

@login_required
def submit_feedback(request, request_id):
    """Tenant submits their monthly feedback."""
    feedback_req = get_object_or_404(FeedbackRequest, id=request_id, status='PENDING')
    
    # Security Check
    if request.user != feedback_req.contract.booking.tenant:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        maintenance_rating = request.POST.get('maintenance_rating', 5)
        responsiveness_rating = request.POST.get('responsiveness_rating', 5)
        safety_rating = request.POST.get('safety_rating', 5)
        vibe_rating = request.POST.get('vibe_rating', 5)
        comments = request.POST.get('comments', '')
        
        MonthlyFeedback.objects.create(
            feedback_request=feedback_req,
            property=feedback_req.contract.booking.property,
            tenant=request.user,
            maintenance_rating=maintenance_rating,
            responsiveness_rating=responsiveness_rating,
            safety_rating=safety_rating,
            vibe_rating=vibe_rating,
            comments=comments
        )
        
        feedback_req.status = 'COMPLETED'
        feedback_req.save()
        
        messages.success(request, "Thank you! Your monthly feedback has been submitted.")
        return redirect('tenant:dashboard')
        
    return render(request, 'feedback/submit_form.html', {'feedback_request': feedback_req})
