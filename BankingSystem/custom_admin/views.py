from rest_framework import generics
from .models import AccountInfo
from .serializers import AccountInfoSerializer
from rest_framework.permissions import AllowAny,IsAdminUser


class AccountInfoAPIView(generics.ListCreateAPIView):
    queryset = AccountInfo.objects.all()
    serializer_class = AccountInfoSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save() 


class AccountInfoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountInfo.objects.all()
    serializer_class = AccountInfoSerializer
    permission_classes = [IsAdminUser] 