from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import requests

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

@method_decorator(csrf_exempt, name='dispatch')
class AssistantView(APIView):
    def post(self, request):
        user_input = request.data.get("message", "")
        if not user_input:
            return Response({"error": "No message provided"}, status=400)

        if not MISTRAL_API_KEY:
            return Response({"error": "MISTRAL_API_KEY is not configured in your environment."}, status=500)

        try:
            headers = {
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "mistral-medium",  # or mistral-small
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Zuply Assistant, an AI helping users with food donation, food waste reduction, redistribution, and sustainability in India."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }

            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )

            json_response = response.json()
            reply = json_response.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not reply:
                return Response({"error": "Mistral API returned an empty response."}, status=502)

            return Response({"reply": reply}, status=200)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Network error: {str(e)}"}, status=503)

        except Exception as e:
            return Response({"error": f"Server error: {str(e)}"}, status=500)
