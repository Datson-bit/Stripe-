from django.contrib import admin
from .models import Donation, Payment


admin.site.register(Donation)
admin.site.register(Payment)