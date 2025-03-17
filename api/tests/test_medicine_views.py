from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from api.models import Medicine
from api.tests.factories import MedicineFactory, UserFactory


class TestMedicineListCreateView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.inventory_manager = UserFactory(role="inventory_manager")
        self.inventory_manager.set_password("inventorypass")
        self.inventory_manager.save()

        self.staff_user = UserFactory(role="staff")
        self.staff_user.set_password("staffpass")
        self.staff_user.save()

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.inventory_manager.username, "password": "inventorypass"},
        )
        self.inventory_manager_token = response.data.get("access")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.staff_user.username, "password": "staffpass"},
        )
        self.staff_token = response.data.get("access")

        self.medicine_list_url = reverse("medicines-create-list")

    def test_authenticated_user_can_list_medicines(self):
        """Ensure authenticated users can retrieve medicine list."""
        MedicineFactory.create_batch(3)

        response = self.client.get(
            self.medicine_list_url,
            HTTP_AUTHORIZATION=f"Bearer {self.staff_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_authenticated_user_can_create_medicine(self):
        """Ensure non-inventory managers get 403 Forbidden when adding medicine."""
        payload = {
            "name": "Ibuprofen",
            "description": "Anti-inflammatory tablet",
            "category": "Painkiller",
            "stock": 30,
            "expiry_date": "2026-06-30",
            "packaging_type": "strip",
            "price": "12.99",
        }

        response = self.client.post(
            self.medicine_list_url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.inventory_manager_token}"
        )

        self.assertEqual(response.status_code, 201)

    def test_non_inventory_manager_cannot_create_medicine(self):
        """Ensure non-inventory managers get 403 Forbidden when adding medicine."""
        payload = {
            "name": "Ibuprofen",
            "description": "Anti-inflammatory tablet",
            "category": "Painkiller",
            "stock": 30,
            "expiry_date": "2026-06-30",
            "packaging_type": "strip",
            "price": "12.99",
        }

        response = self.client.post(
            self.medicine_list_url,
            data=payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.staff_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.medicine_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestMedicineDetailView(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.inventory_manager = UserFactory(role="inventory_manager")
        self.inventory_manager.set_password("inventorypass")
        self.inventory_manager.save()

        self.staff_user = UserFactory(role="staff")
        self.staff_user.set_password("staffpass")
        self.staff_user.save()

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.inventory_manager.username, "password": "inventorypass"},
        )
        self.inventory_manager_token = response.data.get("access")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.staff_user.username, "password": "staffpass"},
        )
        self.staff_token = response.data.get("access")

        self.medicine = MedicineFactory()
        self.medicine_detail_url = reverse("medicines-detail", kwargs={"pk": self.medicine.id})

    def test_authenticated_user_can_retrieve_medicine(self):
        """Ensure authenticated users can retrieve medicine details."""
        response = self.client.get(
            self.medicine_detail_url,
            HTTP_AUTHORIZATION=f"Bearer {self.staff_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.medicine.name)

    def test_inventory_manager_can_update_medicine(self):
        """Ensure only inventory managers can update medicine details."""
        update_payload = {
            "name": "Updated Medicine",
            "stock": 75,
            "price": "19.99"
        }

        response = self.client.put(
            self.medicine_detail_url,
            data=update_payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.inventory_manager_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Updated Medicine")
        self.assertEqual(response.data["data"]["stock"], 75)

    def test_non_inventory_manager_cannot_update_medicine(self):
        """Ensure non-inventory managers get 403 Forbidden when updating."""
        update_payload = {
            "name": "Wrong Update",
            "stock": 10
        }

        response = self.client.put(
            self.medicine_detail_url,
            data=update_payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.staff_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inventory_manager_can_delete_medicine(self):
        """Ensure inventory managers can delete medicine."""
        response = self.client.delete(
            self.medicine_detail_url,
            HTTP_AUTHORIZATION=f"Bearer {self.inventory_manager_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["message"], f"Medicine '{self.medicine.name}' deleted successfully.")
        self.assertFalse(Medicine.objects.filter(id=self.medicine.id).exists())

    def test_non_inventory_manager_cannot_delete_medicine(self):
        """Ensure non-inventory managers get 403 Forbidden when deleting."""
        response = self.client.delete(
            self.medicine_detail_url,
            HTTP_AUTHORIZATION=f"Bearer {self.staff_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.medicine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)