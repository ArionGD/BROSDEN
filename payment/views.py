from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import KYCForm
from .models import KYC

@login_required
def kyc_form_view(request):
    """View to handle common KYC registration for both roles."""
    try:
        kyc = request.user.kyc
        if kyc.is_verified:
            messages.info(request, "Your KYC is already verified.")
            return redirect('index')
    except KYC.DoesNotExist:
        kyc = None

    if request.method == 'POST':
        form = KYCForm(request.POST, instance=kyc)
        if form.is_valid():
            kyc_obj = form.save(commit=False)
            kyc_obj.user = request.user
            # For this demo, we auto-verify to keep it smooth
            kyc_obj.is_verified = True 
            kyc_obj.save()
            messages.success(request, "KYC submitted and verified successfully!")
            
            # Check where they came from
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')
    else:
        form = KYCForm(instance=kyc)
    
    return render(request, 'payment/kyc_form.html', {'form': form})

@login_required
def razorpay_checkout(request):
    """Interface mimicking Razorpay payment process."""
    amount = request.GET.get('amount', '500')
    item = request.GET.get('item', 'Security Deposit')
    
    context = {
        'amount': amount,
        'item': item,
        'user': request.user
    }
    return render(request, 'payment/razorpay_interface.html', context)
