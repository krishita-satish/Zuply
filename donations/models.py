from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Donation(models.Model):
    FOOD_TYPES = [
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
        ('mixed', 'Mixed'),
    ]

    SPICE_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('picked', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('composted', 'Composted'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.CharField(max_length=255)
    food_type = models.CharField(max_length=10, choices=FOOD_TYPES, default='veg')
    spice_level = models.CharField(max_length=10, choices=SPICE_LEVELS, default='medium')
    quantity_kg = models.FloatField()
    pickup_address = models.TextField()
    pincode = models.CharField(max_length=10)
    expiry_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    is_collected = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    is_emergency = models.BooleanField(default=False)
    qr_code = models.CharField(max_length=255, blank=True)
    
    # Optional: To log who receives it
    matched_recipient_id = models.IntegerField(null=True, blank=True)

    # Optional: To log ML score
    donation_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.food_item} ({self.quantity_kg}kg) by {self.donor.username}"
