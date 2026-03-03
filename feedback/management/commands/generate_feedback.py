from django.core.management.base import BaseCommand
from django.utils import timezone
from contract.models import Contract
from feedback.models import FeedbackRequest

class Command(BaseCommand):
    help = 'Generates monthly feedback requests for active contracts'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Get all signed, active contracts
        active_contracts = Contract.objects.filter(is_signed_by_tenant=True, is_signed_by_owner=True)
        
        created_count = 0
        for contract in active_contracts:
            start_date = contract.created_at.date() # Simplified: using creation date as anniversary marker
            
            # If today is exactly 1 month, 2 months, etc. after start_date
            if start_date.day == today.day and start_date < today:
                # Check if we already created one for this contract today
                defaults = {'status': 'PENDING'}
                obj, created = FeedbackRequest.objects.get_or_create(
                    contract=contract,
                    due_date=today,
                    defaults=defaults
                )
                if created:
                    created_count += 1
                    
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {created_count} feedback requests for {today}.'))
