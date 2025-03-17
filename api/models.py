from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('inventory_manager', 'Inventory Manager'),
        ('staff', 'Staff'),
    ]
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Medicine(models.Model):
    PACKAGING_CHOICES = [
        ('single', 'Single'),
        ('strip', 'Strip'),
        ('pack', 'Pack'),
        ('box', 'Box'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    expiry_date = models.DateField()
    packaging_type = models.CharField(max_length=10, choices=PACKAGING_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.packaging_type})"

class Bill(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bills")
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="bills")
    quantity = models.PositiveIntegerField()
    packaging_type = models.CharField(max_length=10, choices=[
        ('single', 'Single'),
        ('strip', 'Strip'),
        ('pack', 'Pack'),
        ('box', 'Box'),
    ])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill {self.id} - {self.medicine.name} ({self.quantity} {self.packaging_type})"