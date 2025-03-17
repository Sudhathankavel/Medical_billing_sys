from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from api.tests.factories import UserFactory
from rest_framework import status

User = get_user_model()

class TestUserRegistration(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            password="adminpass",
            email="admin@example.com"
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "adminuser", "password": "adminpass"},
        )

        self.token = response.data.get("access")
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}
    def test_admin_can_register_users(self):
        """Ensure an admin can register new staff or inventory managers"""
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "username": "staff_user",
            "password": "password123",
            "full_name": "Staff User",
            "phone_number": "+1234567890",
            "role": "staff"
        }

        response = self.client.post(
            "/api/auth/register/",
            payload,
            format="json",
            headers=self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # ✅ Use Django's assertEqual
        self.assertEqual(response.data["message"], "User registered successfully!")
        self.assertEqual(response.data["user"]["username"], "staff_user")
        self.assertEqual(response.data["user"]["role"], "staff")

    def test_non_admin_cannot_register_users(self):
        """Ensure non-admin users cannot register new users"""
        staff_user = UserFactory(role="staff")
        self.client.force_authenticate(user=staff_user)

        payload = {
            "username": "new_user",
            "password": "password123",
            "role": "staff"
        }
        response = self.client.post("/api/auth/register/", payload)

        assert response.status_code == 403  # Forbidden

    def test_register_without_authentication(self):
        """Ensure unauthenticated users cannot register new users"""
        payload = {
            "username": "new_user",
            "password": "password123",
            "role": "staff"
        }
        response = self.client.post("/api/auth/register/", payload)

        assert response.status_code == 401

class TestUserListView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = UserFactory(
            username="adminuser",
            password="adminpass",
            full_name="admin@example.com",
            role = 'admin'
        )

        self.non_admin_user = UserFactory(
            username="testuser",
            password="testpass",
            full_name="user@example.com",
            role = 'staff'
        )
        self.user_list_url = reverse("user-list")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "adminuser", "password": "adminpass"},
        )
        self.admin_token = response.data.get("access")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass"},
        )
        self.non_admin_token = response.data.get("access")

    def test_admin_can_view_users(self):
        """ Ensure an admin can access the user list."""
        response = self.client.get(
            self.user_list_url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_view_users(self):
        """Ensure non-admin users get 403 Forbidden."""
        response = self.client.get(
            self.user_list_url,
            HTTP_AUTHORIZATION=f"Bearer {self.non_admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_view_users(self):
        """❌ Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserDetailView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = UserFactory(
            username="adminuser",
            password="adminpass",
            full_name="Admin User",
            role="admin"
        )
        self.non_admin_user = UserFactory(
            username="testuser",
            password="testpass",
            full_name="Non-Admin User",
            role="staff"
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "adminuser", "password": "adminpass"},
        )
        self.admin_token = response.data.get("access")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass"},
        )
        self.non_admin_token = response.data.get("access")
        self.target_user = UserFactory(username="targetuser", role="staff")
        self.user_detail_url = reverse("user-detail", kwargs={"pk": self.target_user.id})

    def test_admin_can_view_user_detail(self):
        """Ensure an admin can retrieve user details."""
        response = self.client.get(
            self.user_detail_url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.target_user.username)

    def test_non_admin_cannot_view_user_detail(self):
        """Ensure non-admin users get 403 Forbidden."""
        response = self.client.get(
            self.user_detail_url,
            HTTP_AUTHORIZATION=f"Bearer {self.non_admin_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_view_user_detail(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestUserUpdateView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = UserFactory(
            username="adminuser",
            password="adminpass",
            full_name="Admin User",
            role="admin"
        )
        self.non_admin_user = UserFactory(
            username="testuser",
            password="testpass",
            full_name="Non-Admin User",
            role="staff"
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "adminuser", "password": "adminpass"},
        )
        self.admin_token = response.data.get("access")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass"},
        )
        self.non_admin_token = response.data.get("access")

        self.target_user = UserFactory(username="targetuser", role="staff")
        self.user_update_url = reverse("user-update", kwargs={"pk": self.target_user.id})

    def test_admin_can_update_user(self):
        """Ensure an admin can update a user's details."""
        payload = {"full_name": "Updated User", "role": "inventory_manager"}

        response = self.client.patch(
            self.user_update_url,
            payload,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.full_name, "Updated User")
        self.assertEqual(self.target_user.role, "inventory_manager")

    def test_non_admin_cannot_update_user(self):
        """Ensure non-admin users get 403 Forbidden."""
        payload = {"full_name": "Updated User"}

        response = self.client.patch(
            self.user_update_url,
            payload,
            HTTP_AUTHORIZATION=f"Bearer {self.non_admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_user(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        payload = {"full_name": "Updated User"}

        response = self.client.patch(self.user_update_url, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestUserDeleteView(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = UserFactory(
            username="adminuser",
            password="adminpass",
            full_name="Admin User",
            role="admin"
        )
        self.non_admin_user = UserFactory(
            username="testuser",
            password="testpass",
            full_name="Non-Admin User",
            role="staff"
        )

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "adminuser", "password": "adminpass"},
        )
        self.admin_token = response.data.get("access")

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpass"},
        )
        self.non_admin_token = response.data.get("access")

        self.target_user = UserFactory(username="targetuser", role="staff")
        self.user_delete_url = reverse("user-delete", kwargs={"pk": self.target_user.id})

    def test_admin_can_delete_user(self):
        """Ensure an admin can delete a user."""
        response = self.client.delete(
            self.user_delete_url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "User deleted successfully")
        self.assertFalse(User.objects.filter(id=self.target_user.id).exists())

    def test_non_admin_cannot_delete_user(self):
        """Ensure non-admin users get 403 Forbidden."""
        response = self.client.delete(
            self.user_delete_url,
            HTTP_AUTHORIZATION=f"Bearer {self.non_admin_token}"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(id=self.target_user.id).exists())

    def test_unauthenticated_user_cannot_delete_user(self):
        """Ensure unauthenticated users get 401 Unauthorized."""
        response = self.client.delete(self.user_delete_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(id=self.target_user.id).exists())