from celery import shared_task
from datetime import date
from dateutil.relativedelta import relativedelta

from Base_Panel.models import Hostler
from Base_Panel.models import Transaction


@shared_task
def generate_monthly_bills():

    hostlers = Hostler.objects.filter(is_active=True)

    for hostler in hostlers:

        last_transaction = Transaction.objects.filter(
            hostler=hostler
        ).order_by("-billing_date").first()

        if not last_transaction:
            continue

        next_billing_date = (
            last_transaction.billing_date +
            relativedelta(months=1)
        )

        already_exists = Transaction.objects.filter(
            hostler=hostler,
            billing_date=next_billing_date
        ).exists()

        if already_exists:
            continue

        if date.today() >= next_billing_date:

            Transaction.objects.create(
                hostler=hostler,
                amount=hostler.monthly_rent,
                payment_type="rent",
                status="pending",
                billing_date=next_billing_date,
                due_date=next_billing_date
            )

            print(f"Bill created for {hostler.user.username}")

    return "Monthly Bills Generated"


from django.utils import timezone

from .models import AssignedMeal


@shared_task
def lock_expired_meals():

    meals = AssignedMeal.objects.filter(
        response_deadline__lt=timezone.now(),
        is_locked=False
    )

    updated_count = meals.update(
        is_locked=True
    )

    return f"{updated_count} meals locked"