import random
from datetime import date, timedelta, timezone, datetime

import factory
from django.contrib.auth import get_user_model

from api.models import Medicine, Bill

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    full_name = factory.Faker("name")
    phone_number = factory.Faker("phone_number")
    role = "staff"

class MedicineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Medicine

    name = factory.Faker("company")
    description = factory.Faker("sentence")
    category = factory.Faker("word")
    stock = factory.LazyFunction(lambda: random.randint(1, 100))
    expiry_date = factory.LazyFunction(
        lambda: date.today() + timedelta(days=random.randint(30, 365)))
    packaging_type = factory.LazyFunction(
        lambda: random.choice([choice[0] for choice in Medicine.PACKAGING_CHOICES]))
    price = factory.LazyFunction(lambda: round(random.uniform(10.0, 500.0), 2))


class BillFactory(factory.django.DjangoModelFactory):
    """Factory for creating Bill instances."""
    class Meta:
        model = Bill

    staff = factory.SubFactory(UserFactory)
    medicine = factory.SubFactory(MedicineFactory)
    quantity = factory.Faker("random_int", min=1, max=10)
    packaging_type = factory.LazyAttribute(lambda obj: obj.medicine.packaging_type)
    total_price = factory.LazyAttribute(lambda obj: obj.medicine.price * obj.quantity)
    created_at = factory.LazyFunction(datetime.now(timezone.utc))