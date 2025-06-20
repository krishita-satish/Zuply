from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('food_item', 'donor', 'quantity_kg', 'status', 'is_emergency', 'created_at')
    search_fields = ('food_item', 'donor__username', 'pincode')
    list_filter = ('status', 'is_emergency', 'food_type', 'spice_level')

