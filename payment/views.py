from django.shortcuts import render
from django.http import HttpResponse
import stripe.error
from .models import Donation, Payment
from django.shortcuts import get_object_or_404
import stripe
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

def donations(request):
    donations = Donation.objects.all()
    return render (request, 'donations.html', {'donations':donations})


def checkout(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'checkout.html', {'donation':donation})


def create_checkout_session(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email = request.user.email if request.user.is_authenticated else None,
            line_items=[{
                "price_data":{
                    "currency":"usd",
                    "product_data":{
                        "name":donation.title,
                        "images":[donation.img_url]
                    },
                    "unit_amount": int(donation.amount*100)
                },
                "quantity":1,
            }],
            mode="payment",
            success_url= f"http://localhost:8000/payment-success?session_id={{CHECKOUT_SESSION_ID}}&donation_id={donation.id}",
            cancel_url = "http://localhost:8000/payment-failed"
        )
        return JsonResponse({"checkout_url":session.url})
    
    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)}, status=400)
    

def payment_success(request):
    session_id = request.GET.get("session_id")
    donation_id = request.GET.get("donation_id")

    if not session_id or not donation_id:
        return JsonResponse({"error": "Invalid session"}, staus=400)
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        donation = get_object_or_404(Donation, id=donation_id)

        customer_email = session.customer_email or session.customer_details.get("email", "")
        customer_name = session.customer_details.name

        if session.payment_status == "paid":
            Payment.objects.create(
                donation=donation,
                customer_name = session.customer_details.name,
                customer_email =customer_email,
                amount= session.amount_total/100,
                payment_intent_id= session.payment_intent,
                status="completed",
            )
            return render(request, 'payment_success.html', {'customer_name':customer_name})
        
        return JsonResponse({'error': "Payment not completed"}, status= 400)
    
    except stripe.error.StripeError as e:
        return JsonResponse({"error":str(e)}, status=400)
    

def payment_failed(request):
    error_message = request.GET.get("error", "Your payment could not be processed. Please try again")

    return render(request, "payment_failed.html", {'error_message':error_message})


endpoint_secret = "whsec_a1bf114be69f862cddc39cf463fbd9b6744402e06ac451038348305d9afc2fe9"

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    print("Received event:", json.loads(payload))

    return JsonResponse({"status": "success"}, status=200)

