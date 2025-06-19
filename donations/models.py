from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # ✅ Good — used for default timestamps

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.CharField(max_length=255)
    quantity_kg = models.FloatField()
    pickup_address = models.TextField()
    expiry_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)  # ✅ Perfect for tracking when donated
    is_collected = models.BooleanField(default=False)
    qr_code = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.food_item} ({self.quantity_kg}kg) by {self.donor.username}"
