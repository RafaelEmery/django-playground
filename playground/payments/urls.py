from rest_framework.routers import path

from .views import (
    CustomerAPIView,
    CustomerBalanceAPIView,
    CustomerDetailAPIView,
    TransactionAPIView,
)

urlpatterns = [
    path("customers/", CustomerAPIView.as_view(), name="customers"),
    path("customers/<uuid:id>/", CustomerDetailAPIView.as_view(), name="customer-details"),
    path("customers/<uuid:id>/balance/", CustomerBalanceAPIView.as_view(), name="customer-balance"),
    path("transactions/", TransactionAPIView.as_view(), name="transactions")
]


