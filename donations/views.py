from rest_framework import viewsets
from .models import Donation
from .serializers import DonationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ai_ml.prioritization_model import process_request  # ✅ Corrected import based on ai_ml folder
from django.utils import timezone

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Save donation first so we can score it
        donation = serializer.save()

        # Placeholder user profile info (later pull from actual user model)
        user_data = {
            "user_id": self.request.user.id,
            "family_size": 4,  # TODO: Replace with real data from profile
            "last_donation": timezone.now() - timezone.timedelta(hours=20),  # Example value
            "feedback_score": 4.5,  # Placeholder
            "urgency_flag": donation.is_emergency,
            "special_needs": None,
            "dietary_preference": donation.food_type,
        }

        # Run AI scoring
        result = process_request(
            user=user_data,
            food_stock_level=120,  # TODO: Dynamic logic later
            current_time=timezone.now(),
            pincode=donation.pincode,
            is_festival=False
        )

        # Save updated score
        donation.donation_score = result["score"]
        donation.save()
