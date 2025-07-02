from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from donations.views import DonationViewSet, AssistantView  # ✅ Import both views

# DRF Router for DonationViewSet
router = routers.DefaultRouter()
router.register(r'donations', DonationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),               # ✅ Admin panel
    path('api/', include(router.urls)),            # ✅ Donation API endpoints (CRUD)
    path('assistant/', AssistantView.as_view()),   # ✅ AI Assistant (text-based Q&A via Mistral)
]
