from rest_framework.routers import path

from .views import CustomerAPIView

urlpatterns = [
    path("customers/", CustomerAPIView.as_view(), name="Customers")
]


