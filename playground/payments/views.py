import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Balance, Customer, Transaction
from .serializers import BalanceSerializer, CustomerSerializer, TransactionSerializer


class CustomerAPIView(APIView):
    def get(self, request):
        # TODO: include query params and query params validation
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)

        return Response(serializer.data)

    # TODO: validate and try to set transaction on customer and balance creation
    def post(self, request):
        """
        Creates a new customer with default balance.
        """
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()

        # TODO: use signals/post_create or post_save function to create balance
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


class CustomerDetailAPIView(APIView):
    def get(self, request, id):
        customer = get_object_or_404(Customer, id=id)
        serializer = CustomerSerializer(customer)

        return Response(serializer.data)

class CustomerBalanceAPIView(APIView):
    def get(self, request, id):
        balance = Balance.objects.filter(customer__id=id).first()
        if not balance:
            return Response(
                {"detail": "Balance not found for this customer."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = BalanceSerializer(balance)

        return Response(serializer.data)


class TransactionAPIView(APIView):
    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)

        return Response(serializer.data)
