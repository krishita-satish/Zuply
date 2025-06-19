from rest_framework import viewsets
from .models import Donation
from .serializers import DonationSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


