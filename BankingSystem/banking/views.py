from rest_framework import status,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from accounts.models import *
from .serializers import *
from rest_framework.permissions import AllowAny,IsAdminUser
from django.core.exceptions import ValidationError
from random import randint
from django.db import transaction
from django.utils import timezone
from datetime import timedelta,date
from django.db.models import F,Sum
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404


class CreateAccountAPIView(APIView):

    MAX_ACCOUNTS_PER_TYPE = 4

    def generate_account_number(self):
        return ''.join(["{}".format(randint(0, 9)) for num in range(0, 10)])

    def check_account_limit(self, user_profile, account_type):
        existing_count = Account.objects.filter(user=user_profile, account_type=account_type).count()
        if existing_count >= self.MAX_ACCOUNTS_PER_TYPE:
            raise ValidationError(f'Maximum {self.MAX_ACCOUNTS_PER_TYPE} accounts allowed for {account_type} account type')

    def get_account_type(self, account_number):
        try:
            account = Account.objects.get(account_number=account_number)
            return account.account_type
        except Account.DoesNotExist:
            return None

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        
        if serializer.is_valid():
            user_profile = request.user

            if user_profile:
                serializer.validated_data['user'] = user_profile

                account_type = serializer.validated_data.get('account_type')
                if account_type:
                    try:
                        self.check_account_limit(user_profile, account_type)
                    except ValidationError as e:
                        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                    account_number = self.generate_account_number()
                    serializer.validated_data['account_number'] = account_number
                    account = serializer.save()

                    if account_type in ['savings', 'current']:
                        if account_type == 'savings':
                            account_serializer = SavingsAccountSerializer(data=request.data)
                        elif account_type == 'current':
                            account_serializer = CurrentAccountSerializer(data=request.data)
                        
                        if account_serializer.is_valid():
                            account_serializer.validated_data['account'] = account
                            account_serializer.save()
                            return Response({'your account number': account_number, 'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)
                        else:
                            account.delete()
                            return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        
                    if account_type in ['fixed_deposit', 'recurring_deposit']:
                        source_account_number = request.data.get('account_number')
                        source_account_type = self.get_account_type(source_account_number)
                        if source_account_type not in ['savings', 'current']:
                            account.delete()
                            return Response({'error': f' Check your account number. '}, status=status.HTTP_400_BAD_REQUEST)
                        source_account_id = Account.objects.get(account_number=source_account_number).id

                        deposit_account_data = {'account': account} 
                        if account_type == 'fixed_deposit':
                            serializer = FixedDepositAccountSerializer(data=request.data)
                        elif account_type == 'recurring_deposit':
                            serializer = RecurringDepositAccountSerializer(data=request.data)

                        if serializer.is_valid():
                            serializer.validated_data['account'] = account
                            serializer.validated_data['source_account_id'] = source_account_id
    
                            deposit_account_instance = serializer.save()
                            return Response({'Reference Number': account_number, 'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)
                        else:
                            account.delete()
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    return Response({'your account number': account_number, 'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Account type is required'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'User profile does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OpenedAccountListAPIView(generics.ListAPIView):
    serializer_class = AllAccountSerializer

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)


class AccountBalanceAPIView(generics.RetrieveAPIView):
    serializer_class = AccountBalanceSerializer

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DepositFundsAPIView(APIView):
    def post(self, request):
        saving_account_id = request.data.get('saving_account_id')
        account_number = request.data.get('account_number')
        deposit_amount = request.data.get('deposit_amount')
        duration_months = request.data.get('duration_months')

        try:
            saving_account = Account.objects.get(id=saving_account_id)
        except Account.DoesNotExist:
            return Response({'error': 'Saving account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if deposit_amount <= 0:
            return Response({'error': 'Deposit amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        if saving_account.amount < deposit_amount:
            return Response({'error': 'Insufficient funds in the saving account'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            
            destination_account = Account.objects.get(account_number=account_number)
        except Account.DoesNotExist:
            return Response({'error': 'Destination account not found'}, status=status.HTTP_404_NOT_FOUND)

        
        if destination_account.account_type == 'fixed_deposit':
            try:
                deposit_account = FixedDepositAccount.objects.get(account=destination_account)
            except FixedDepositAccount.DoesNotExist:
                return Response({'error': 'Fixed Deposit account not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if deposit_account.duration_months <= 0:
                return Response({'error': 'Fixed Deposit account duration has expired'}, status=status.HTTP_400_BAD_REQUEST)

            if deposit_account.deposit_amount > 0:
                return Response({'error': 'Additional deposit not allowed for an existing Fixed Deposit account'}, status=status.HTTP_400_BAD_REQUEST)

           
            duration_timedelta = timedelta(days=duration_months * 30)  

            deposit_account.deposit_amount = deposit_amount
            deposit_account.duration_months = duration_months
            deposit_account.expiry_date = timezone.now() + duration_timedelta  
            deposit_account.save()
        elif destination_account.account_type == 'recurring_deposit':
            try:
                deposit_account = RecurringDepositAccount.objects.get(account=destination_account)
            except RecurringDepositAccount.DoesNotExist:
                return Response({'error': 'Recurring Deposit account not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if deposit_account.duration_months <= 0:
                return Response({'error': 'Recurring Deposit account duration has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
            

            if deposit_amount != deposit_account.intial_amount:
                return Response({'error': 'Deposit amount must match the monthly deposit amount for a recurring deposit account'}, status=status.HTTP_400_BAD_REQUEST)
            

            with transaction.atomic():
                saving_account.amount -= deposit_amount
                saving_account.save()

                deposit_account.deposit_amount += deposit_amount
                deposit_account.save()
            
            deposit_account.duration_months -= 1
            deposit_account.save()
        else:
            return Response({'error': 'Invalid deposit type'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'Money deposited successfully into {destination_account.account_type.capitalize()} account'}, status=status.HTTP_200_OK)
            

class WithdrawAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        account_number = request.data.get('account_number')
        amount = request.data.get('amount')

        try:
            account = Account.objects.select_for_update().get(account_number=account_number)
        except Account.DoesNotExist:
            return Response({"error": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if account.amount < amount:
            return Response({"error": "Insufficient funds in the account"}, status=status.HTTP_400_BAD_REQUEST)

        account.amount -= amount
        account.save()

        transaction_instance = Transaction.objects.create(sender=account, amount=amount, transaction_date=timezone.now(), description="Withdrawal", status="Completed")
        serializer = TransactionSerializer(transaction_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FundTransferAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        
        sender_account_id = request.data.get('sender')
        receiver_account_number = request.data.get('receiver')
        amount = request.data.get('amount')

        try:
            sender_account = Account.objects.select_for_update().get(id=sender_account_id)
            receiver_account = Account.objects.select_for_update().get(account_number=receiver_account_number)
        except Account.DoesNotExist:
            return Response({"error": "Sender or receiver account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if sender_account.account_type in ['fixed_deposit', 'recurring_deposit']:
            return Response({"error": "Cannot transfer funds from f{account_type}"}, status=status.HTTP_400_BAD_REQUEST)
        if sender_account.account_type == 'savings':
            today = date.today()
            month_transactions = Transaction.objects.filter(sender=sender_account, transaction_date__month=today.month).count()
            if month_transactions >= 5:
                return Response({"error": "Transaction limit exceeded for this month"}, status=status.HTTP_400_BAD_REQUEST)

            today_transactions_amount = Transaction.objects.filter(sender=sender_account, transaction_date__date=today).aggregate(total_amount=Sum('amount'))['total_amount']
            if today_transactions_amount and (today_transactions_amount + amount) > 200000:
                return Response({"error": "Daily transaction amount limit exceeded"}, status=status.HTTP_400_BAD_REQUEST)

            sender_account.transaction_count = F('transaction_count') + 1
            sender_account.save()

        if sender_account.account_number == receiver_account_number:
            return Response({"error": "You cannot transfer funds to your own account"}, status=status.HTTP_400_BAD_REQUEST)
        
        if sender_account.amount < amount:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

        sender_account.amount -= amount
        sender_account.save()
        receiver_account.amount += amount
        receiver_account.save()

        transaction_instance = Transaction.objects.create( sender=sender_account, receiver=receiver_account, amount=amount,user=request.user)
        serializer = TransactionSerializer(transaction_instance)


        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


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
# -----------------------------------------------------------------------------------------------------------------------------------------------------<>
                                    # LOANApplication
# -----------------------------------------------------------------------------------------------------------------------------------------------------<>


class LoanTypeCreate(generics.ListCreateAPIView):
    queryset = LoanType.objects.all()
    serializer_class = LoanTypeSerializer
    permission_classes = [IsAdminUser]  


class LoanApplicationCreate(generics.ListCreateAPIView):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LoanApplicationApproval(generics.UpdateAPIView):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAdminUser]  

    def perform_update(self, serializer):
        status = self.request.data.get('status')
        if status:
            serializer.validated_data['status'] = status
            
            # Send email notification to the user
            loan_application = serializer.instance
            user_email = loan_application.user.email
            subject = "Loan Application Status Update"
            message = f"Dear {loan_application.user.username},\n\nYour loan application is {status}.\n\nRegards,\n Secure Assets Finance"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email], fail_silently=False)

        serializer.save()


class LoanApplicationList(generics.ListAPIView):
    queryset = LoanApplication.objects.order_by('-application_date')
    serializer_class = LoanListSerializer
    permission_classes = [IsAdminUser]  


class UserLoanApplicationList(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        return LoanApplication.objects.filter(user=user)

    
class UserLoanApplicationDetail(generics.RetrieveAPIView):
    serializer_class = LoanApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        return LoanApplication.objects.filter(user=user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['pk'])
        return obj