from rest_framework.routers import path

from .views import (
    CustomerBalanceAPIView,
    CustomerDetailAPIView,
    CustomerListCreateAPIView,
    TransactionListAPIView,
    TransactionProcessAPIView,
)

urlpatterns = [
    path("customers/", CustomerListCreateAPIView.as_view(), name="customers-list-create"),
    path("customers/<uuid:id>/", CustomerDetailAPIView.as_view(), name="customer-details"),
    path("customers/<uuid:id>/balance/", CustomerBalanceAPIView.as_view(), name="customer-balance"),
    path("transactions/", TransactionListAPIView.as_view(), name="transactions"),
    path("transactions/process/", TransactionProcessAPIView.as_view(), name="transactions-process")
]


