from django.db import models


class Donation(models.Model):
    title = models.CharField(max_length=255)
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    img_url = models.CharField(max_length=2025)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class Payment(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=255, default="USD")
    payment_intent_id= models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.amount} {self.currency}- {self.status}"
