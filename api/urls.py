from django.urls import path
from .views import (
    RegisterUserView,
    LogoutView,
    UserListView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    MedicineListCreateView,
    MedicineDetailView,
    StockAvailabilityAPI,
    BillCreateView,
    SalesReportsAPI
)

from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # User Management
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),


    # medicines
    path('medicines/', MedicineListCreateView.as_view(), name='medicines-create-list'),
    path('medicines/<int:pk>/', MedicineDetailView.as_view(), name='medicines-detail'),

    # Billing
    path('billing/', BillCreateView.as_view(), name='create-bill'),

    # stock
    path("dashboard/stock/", StockAvailabilityAPI.as_view(), name="stock-availability"),

    # report
    path("dashboard/reports/", SalesReportsAPI.as_view(), name="sales-reports"),

]
