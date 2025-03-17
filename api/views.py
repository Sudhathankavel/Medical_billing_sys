from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Medicine, Bill
from .serializers import UserSerializer, MedicineSerializer, BillSerializer, StockAvailabilitySerializer, \
    SalesReportSerializer
from .permissions import IsAdminUser, IsInventoryManager, IsStaff
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
import logging
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_date


User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterUserView(generics.CreateAPIView):
    """
    API for Admins to register new users (Staff or Inventory Manager).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({"message": "User registered successfully!", "user": response.data}, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    Logout API that invalidates the JWT token by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)


class MedicineListCreateView(generics.ListCreateAPIView):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsInventoryManager()]
        return super().get_permissions()

class MedicineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsInventoryManager()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        """Handles updating a medicine record"""
        medicine = self.get_object()
        serializer = self.get_serializer(medicine, data=request.data, partial=True)  # Supports partial updates

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Medicine updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Handles deleting a medicine record"""
        medicine = self.get_object()
        medicine_name = medicine.name  # Store the name before deletion
        medicine.delete()
        return Response(
            {"message": f"Medicine '{medicine_name}' deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class BillCreateView(generics.CreateAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsStaff]

    def perform_create(self, serializer):
        """Attach the logged-in Staff user before saving"""
        serializer.save(staff=self.request.user)


class StockAvailabilityAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        medicines = Medicine.objects.all().order_by("name")
        serializer = StockAvailabilitySerializer(medicines, many=True)
        return Response(serializer.data)

class SalesReportsAPI(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        staff_id = request.GET.get("staff_id")

        bills = Bill.objects.all()

        if start_date and end_date:
            bills = bills.filter(created_at__date__range=[start_date, end_date])

        if staff_id:
            bills = bills.filter(staff_id=staff_id)

        serializer = SalesReportSerializer(bills, many=True)
        return Response(serializer.data)