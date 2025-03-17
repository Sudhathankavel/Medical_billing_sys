from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Bill
from api.tests.factories import BillFactory, UserFactory, MedicineFactory


class TestBillCreateView(APITestCase):
    """Test cases for the Bill creation API."""

    def setUp(self):
        self.staff_user = UserFactory(role="staff")
        self.staff_user.set_password("testpass")
        self.staff_user.save()

        self.medicine = MedicineFactory()
        self.bill_create_url = reverse("create-bill")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.staff_user.username, "password": "testpass"},
        )
        self.staff_token = response.data.get("access")

    def test_staff_can_create_bill(self):
        """Ensure a staff user can create a bill successfully."""
        payload = {
            "medicine_id": self.medicine.id,
            "quantity": 2,
            "packaging_type": self.medicine.packaging_type,
        }

        response = self.client.post(
            self.bill_create_url,
            payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.staff_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bill.objects.count(), 1)
        self.assertEqual(response.data["staff"]["id"], self.staff_user.id)
        self.assertEqual(response.data["medicine_id"], self.medicine.id)

    def test_non_staff_cannot_create_bill(self):
        """Ensure non-staff users cannot create a bill."""
        non_staff_user = UserFactory(role="admin")
        non_staff_user.set_password("adminpass")
        non_staff_user.save()

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": non_staff_user.username, "password": "adminpass"},
        )
        non_staff_token = response.data.get("access")

        payload = {
            "medicine": self.medicine.id,
            "quantity": 3,
            "packaging_type": self.medicine.packaging_type,
            "total_price": str(self.medicine.price * 3),
        }

        response = self.client.post(
            self.bill_create_url,
            payload,
            HTTP_AUTHORIZATION=f"Bearer {non_staff_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_bill(self):
        """Ensure unauthenticated users cannot create a bill."""
        payload = {
            "medicine": self.medicine.id,
            "quantity": 1,
            "packaging_type": self.medicine.packaging_type,
            "total_price": str(self.medicine.price),
        }

        response = self.client.post(self.bill_create_url, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
