import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Balance, Customer
from .serializers import BalanceSerializer, CustomerSerializer


class CustomerAPIView(APIView):
    def get(self, request, id):
        customer = get_object_or_404(Customer, id=id)
        serializer = CustomerSerializer(customer)

        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()

        balance_serializer = BalanceSerializer(data={"customer": customer.id})
        balance_serializer.is_valid(raise_exception=True)
        balance = balance_serializer.save()

        logging.info(f"[payments] customer created: {customer.id} | balance created: {balance.id}")
        return Response(
            data={"id": customer.id},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, id):
        customer = get_object_or_404(Customer, id=id)
        balance = get_object_or_404(Balance, customer=customer)

        logging.info(f"[payments] customer deleted: {customer.id} | balance deleted: {balance.id}")
        balance.delete()
        customer.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
