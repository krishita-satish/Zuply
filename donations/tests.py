from django.test import TestCase
from django.contrib.auth.models import User
from .models import Donation
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

class DonationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_donation(self):
        donation = Donation.objects.create(
            donor=self.user,
            food_item="Rice",
            quantity_kg=5.0,
            pickup_address="123 Main St",
            expiry_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertEqual(donation.food_item, "Rice")
        self.assertFalse(donation.is_collected)

class DonationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apitestuser', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_donation_api_post(self):
        data = {
            "donor": self.user.id,
            "food_item": "Bread",
            "quantity_kg": 2,
            "pickup_address": "456 Another St",
            "expiry_time": str(timezone.now() + timezone.timedelta(hours=5))
        }
        response = self.client.post("/api/donations/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

