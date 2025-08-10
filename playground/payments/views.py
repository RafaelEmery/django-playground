from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomerSerializer


class CustomerAPIView(APIView):

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={"id": serializer.data.get("id")},
            status=status.HTTP_201_CREATED
        )
