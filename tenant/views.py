from django.shortcuts import render
from accounts.decorators import tenant_required

@tenant_required
def dashboard(request):
    return render(request, 'tenant/dashboard.html')
