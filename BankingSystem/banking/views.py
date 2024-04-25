from rest_framework import generics, status,serializers
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from decimal import Decimal


class AccountCreateAPIView(APIView):
    def post(self, request, format=None):
        request.data['user'] = request.user.id
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AccountDetailAPIView(generics.RetrieveAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_object(self):
        return super().get_object()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        balance = instance.balance
        response_data = {
            f"Your {instance.get_account_type_display()} account balance is {balance}"
        }
        return Response(response_data)


class DepositFundsAPIView(generics.GenericAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def patch(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = Decimal(amount)
        except ValueError:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        instance.balance += amount
        instance.save()
        return Response({"message": "Funds deposited successfully"}, status=status.HTTP_200_OK)

    def get_object(self):
        user = self.request.user
        queryset = self.get_queryset()
        obj = generics.get_object_or_404(queryset, user=user)
        self.check_object_permissions(self.request, obj)
        return obj


class WithdrawFundsAPIView(generics.UpdateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def patch(self, request, *args, **kwargs):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if account.balance < amount:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
        
        account.balance -= amount
        account.save()
        return Response({"message": "Funds withdrawn successfully"}, status=status.HTTP_200_OK)



class FundTransferAPIView(generics.CreateAPIView):
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver_id')
        amount = request.data.get('amount')

        try:
            sender_account = request.user.account 
        except AttributeError:
            return Response({"error": "User does not have associated account"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver_account = Account.objects.get(id=receiver_id)
        except Account.DoesNotExist:
            return Response({"error": "Receiver account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if sender_account == receiver_account:
            return Response({"error": "You cannot transfer funds to your own account"}, status=status.HTTP_400_BAD_REQUEST)

        if sender_account.balance < amount:
            return Response({"error": "Insufficient funds in sender's account"}, status=status.HTTP_400_BAD_REQUEST)

        sender_account.balance -= amount
        receiver_account.balance += amount

        sender_account.save()
        receiver_account.save()

        transaction = Transaction.objects.create(sender=sender_account, receiver=receiver_account, amount=amount)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer