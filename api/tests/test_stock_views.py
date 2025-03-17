from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from api.tests.factories import UserFactory, MedicineFactory

class TestStockAvailabilityAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = UserFactory(role="admin")
        self.admin_user.set_password("adminpass")
        self.admin_user.save()
        self.admin_token = self.get_token(self.admin_user)

        self.non_admin_user = UserFactory(role="staff")
        self.non_admin_user.set_password("staffpass")
        self.non_admin_user.save()
        self.non_admin_token = self.get_token(self.non_admin_user)

        self.medicine1 = MedicineFactory(name="Aspirin", stock=50)
        self.medicine2 = MedicineFactory(name="Paracetamol", stock=30)

        self.stock_availability_url = reverse("stock-availability")

    def get_token(self, user):
        """Helper function to obtain JWT token"""
        response = self.client.post(
            reverse("token_obtain_pair"), {"username": user.username, "password": "adminpass"}
        )
        return response.data.get("access")

    def test_admin_can_view_stock(self):
        """Ensure an admin can view the stock availability."""
        response = self.client.get(
            self.stock_availability_url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Two medicines should be returned

        self.assertEqual(response.data[0]["name"], "Aspirin")
        self.assertEqual(response.data[1]["name"], "Paracetamol")

    def test_non_admin_cannot_view_stock(self):
        """ Ensure non-admin users get 403 Forbidden."""
        response = self.client.get(
            self.stock_availability_url,
            HTTP_AUTHORIZATION=f"Bearer {self.non_admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_view_stock(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.stock_availability_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
