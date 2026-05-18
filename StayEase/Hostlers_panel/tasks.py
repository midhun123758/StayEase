from celery import shared_task
from datetime import date
from dateutil.relativedelta import relativedelta

from Base_Panel.models import Hostler, MessCharge
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

from .models import AssignedMeal, MealResponse

@shared_task
def create_meal_charges():

    meals = AssignedMeal.objects.filter(
        response_deadline__lte=timezone.now(),
        is_locked=False
    )

    for meal in meals:

        wanted_responses = MealResponse.objects.filter(
            assigned_meal=meal,
            response="WANT"
        )

        for response in wanted_responses:

            MessCharge.objects.get_or_create(
                hostler=response.hostler,
                assigned_meal=meal,
                defaults={
                    "hostel": meal.hostel,
                    "date": meal.date,
                    "meal_type": meal.meal_type,
                    "amount": meal.amount_per_hostler,
                }
            )

        meal.is_locked = True
        meal.save()