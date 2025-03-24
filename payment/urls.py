from django.urls import path
from .views import donations, checkout, create_checkout_session, payment_success, payment_failed, stripe_webhook

urlpatterns = [
    path('', donations, name='donations'),
    path('checkout/<int:donation_id>',checkout, name='checkout'),
    path('create-checkout-session/<int:donation_id>', create_checkout_session, name="create_checkout_session"),
    path('payment-success', payment_success, name="payment-success"),
    path('payment-failed', payment_failed, name="payment-failed"),
    path('stripe/webhook', stripe_webhook, name="stripe_webhook")
]
