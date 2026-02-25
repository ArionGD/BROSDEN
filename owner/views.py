from django.shortcuts import render
from accounts.decorators import owner_required

@owner_required
def dashboard(request):
    return render(request, 'owner/dashboard.html')
