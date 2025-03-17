from rest_framework import serializers
from django.contrib.auth import get_user_model

from api.models import Medicine, Bill

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'full_name' , 'phone_number', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', 'staff')  # Default role is 'staff'
        )
        return user


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

    def create(self, validated_data):
        return Medicine.objects.create(**validated_data)

class BillSerializer(serializers.ModelSerializer):
    medicine_id = serializers.IntegerField()
    staff = UserSerializer(required = False)
    class Meta:
        model = Bill
        fields = ['id', 'staff','medicine_id', 'quantity', 'packaging_type', 'total_price', 'created_at']
        read_only_fields = ['total_price', 'created_at']

    def create(self, validated_data):
        medicine_id = validated_data.pop('medicine_id')
        try:
            medicine = Medicine.objects.get(id=medicine_id)
        except Medicine.DoesNotExist:
            raise serializers.ValidationError({"medicine_id": "Medicine not found."})

        # Get the correct price based on packaging type
        packaging_type = validated_data.get('packaging_type')
        if medicine.packaging_type != packaging_type:
            raise serializers.ValidationError({"packaging_type": "Invalid packaging type or price not set."})

        price_per_unit = getattr(medicine, 'price')
        quantity = validated_data.get('quantity')

        # Auto-calculate total price
        total_price = price_per_unit * quantity
        validated_data['medicine'] = medicine
        validated_data['total_price'] = total_price
        return super().create(validated_data)

    def get_medicine_id(self, obj):
        return obj.medicine.id


class StockAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ["id", "name", "stock"]

class SalesReportSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.username", read_only=True)
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)

    class Meta:
        model = Bill
        fields = ["id", "staff_name", "medicine_name", "quantity", "packaging_type", "total_price", "created_at"]