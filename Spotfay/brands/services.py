import stripe
from django.conf import settings
from .models import Customer

stripe.api_key = settings.STRIPE_SECRET_KEY

def get_or_create_stripe_customer(user):
    try:
        customer = Customer.objects.get(user=user)
        return customer.stripe_customer_id
    except Customer.DoesNotExist:
        stripe_customer = stripe.Customer.create(email=user.email)
        customer = Customer.objects.create(user=user, stripe_customer_id=stripe_customer.id)
        return stripe_customer.id