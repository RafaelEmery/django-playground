from rest_framework.routers import path

from .views import CustomerAPIView

urlpatterns = [
    path("customers/", CustomerAPIView.as_view(), name="customers"),
    path("customers/<uuid:id>/", CustomerAPIView.as_view(), name="customer-details")
]


