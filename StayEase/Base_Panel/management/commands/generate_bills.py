from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from Base_Panel.models import Hostler, Transaction

class Command(BaseCommand):
    help = "Checks if 30 days have passed and generates next month's bill"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        hostlers = Hostler.objects.filter(is_active=True)
        count = 0

        for h in hostlers:
            # Find the most recent bill for this hostler
            last_bill = Transaction.objects.filter(hostler=h).order_by('-billing_date').first()

            if last_bill:
                # If today is 30 days or more after the last billing date
                if today >= (last_bill.billing_date + timedelta(days=30)):
                    Transaction.objects.create(
                        hostler=h,
                        amount=h.monthly_rent,
                        status='pending',
                        billing_date=today
                    )
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {count} bills."))