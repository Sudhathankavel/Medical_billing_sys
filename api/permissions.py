from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Allows access only to Admin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsInventoryManager(BasePermission):
    """Custom permission to allow only Inventory Managers to modify medicines."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'inventory_manager'

class IsStaff(BasePermission):
    """Allow only Staff to create bills"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'staff'