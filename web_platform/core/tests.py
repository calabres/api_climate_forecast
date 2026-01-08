from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class APITests(APITestCase):
    def test_skill_endpoint_exists(self):
        """Test that the skill API endpoint exists and requires parameters"""
        url = reverse('api_skill')
        response = self.client.get(url)
        # It should return 400 because parameters are missing, but it proves the endpoint is wired up
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_smart_forecast_endpoint_exists(self):
        """Test that the smart forecast API endpoint exists"""
        url = reverse('api_smart_forecast')
        response = self.client.get(url)
        # Similar logic: proves connectivity
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_docs_page(self):
        """Test that the Swagger UI page loads"""
        url = reverse('swagger-ui')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
