from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from api.tests.factories import UserFactory, MedicineFactory, BillFactory

class TestSalesReportsAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = UserFactory(role="admin")
        self.admin_user.set_password("adminpass")
        self.admin_user.save()
        self.admin_token = self.get_token(self.admin_user)

        self.staff_user = UserFactory(role="staff")
        self.staff_user.set_password("staffpass")
        self.staff_user.save()
        self.staff_token = self.get_token(self.staff_user)
        self.medicine = MedicineFactory(name="Paracetamol", price=5.00)

        self.bill1 = BillFactory(staff=self.staff_user, medicine=self.medicine, created_at=now() - timedelta(days=5))
        self.bill2 = BillFactory(staff=self.staff_user, medicine=self.medicine, created_at=now() - timedelta(days=2))
        self.bill3 = BillFactory(staff=self.admin_user, medicine=self.medicine, created_at=now())

        self.sales_reports_url = reverse("sales-reports")  # Define this in your URLs

    def get_token(self, user):
        """Helper function to obtain JWT token"""
        response = self.client.post(
            reverse("token_obtain_pair"), {"username": user.username, "password": "adminpass"}
        )
        return response.data.get("access")

    def test_admin_can_view_sales_reports(self):
        """Ensure an admin can view sales reports."""
        response = self.client.get(
            self.sales_reports_url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_sales_reports_filtered_by_date_range(self):
        """Ensure sales reports can be filtered by date range."""
        start_date = (now() - timedelta(days=4)).date()
        end_date = now().date()

        response = self.client.get(
            self.sales_reports_url,
            {"start_date": start_date, "end_date": end_date},
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_sales_reports_filtered_by_staff(self):
        """Ensure sales reports can be filtered by staff ID."""
        response = self.client.get(
            self.sales_reports_url,
            {"staff_id": self.staff_user.id},
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only bill1 and bill2 belong to the staff user

    def test_non_admin_cannot_view_sales_reports(self):
        """Ensure non-admin users get 403 Forbidden."""
        response = self.client.get(
            self.sales_reports_url,
            HTTP_AUTHORIZATION=f"Bearer {self.staff_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_view_sales_reports(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.sales_reports_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
