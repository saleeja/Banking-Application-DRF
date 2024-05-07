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
from accounts.permissions import IsStaffUser
from rest_framework.pagination import LimitOffsetPagination
from django.http import HttpResponse
from .utils import generate_account_statement_pdf
from datetime import datetime


class CreateAccountAPIView(APIView):

    MAX_ACCOUNTS_PER_TYPE = 13

    def check_account_limit(self, user_profile, account_type):
        existing_count = Account.objects.filter(user=user_profile, account_type=account_type).count()
        if existing_count >= self.MAX_ACCOUNTS_PER_TYPE:
            raise ValidationError(f'Maximum {self.MAX_ACCOUNTS_PER_TYPE} accounts allowed for {account_type} account type')

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
                    
                    account = serializer.save()

                    if account_type in ['savings', 'current']:
                        if account_type == 'savings':
                            account_serializer = SavingsAccountSerializer(data=request.data)
                        elif account_type == 'current':
                            account_serializer = CurrentAccountSerializer(data=request.data)
                        
                        if account_serializer.is_valid():
                            account_serializer.validated_data['account'] = account
                            account_serializer.save()
                            response_data = {
                                'message': 'Account created successfully',
                                'Your account number is': account.account_number  
                            }
                            return Response(response_data, status=status.HTTP_201_CREATED)
                        else:
                            account.delete()
                            return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    elif account_type in ['fixed_deposit', 'recurring_deposit']:
                        source_account_id = request.data.get('source_account_id')  # Assuming source_account_id is provided in request data
                        try:
                            source_account = Account.objects.get(id=source_account_id, user=user_profile)
                        except Account.DoesNotExist:
                            return Response({'error': 'Invalid account ID.'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        source_account_type = source_account.account_type
                        if source_account_type not in ['savings', 'current']:
                            return Response({'error': 'Selected account is not a savings or current account.'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        if account_type == 'fixed_deposit':
                            serializer = FixedDepositAccountSerializer(data=request.data)
                        elif account_type == 'recurring_deposit':
                            serializer = RecurringDepositAccountSerializer(data=request.data)

                        if serializer.is_valid():
                            serializer.validated_data['account'] = account
                            serializer.validated_data['source_account_id'] = source_account_id
                            serializer.save()
                            response_data = {
                                'message': 'Account created successfully',
                                'Your account number is': account.account_number  
                            }
                            return Response(response_data, status=status.HTTP_201_CREATED)
                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        return Response({'error': 'User profile does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OpenedAccountListAPIView(generics.ListAPIView):
    serializer_class = AllAccountSerializer

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)


class AccountInfoAPIView(generics.ListCreateAPIView):
    queryset = AccountInfo.objects.all()
    serializer_class = AccountInfoSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'message': 'Account info created successfully.'}, status=status.HTTP_201_CREATED)

class AccountInfoDeleteView(generics.DestroyAPIView):
    queryset = AccountInfo.objects.all()
    serializer_class = AccountInfoSerializer
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Account info deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
class AccountInfoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountInfo.objects.all()
    serializer_class = AccountInfoSerializer
    permission_classes = [IsAdminUser] 
    

class AuthAccountListView(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAdminUser | IsStaffUser]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        
        name = self.request.query_params.get('name')
        account_number = self.request.query_params.get('account_number')
        
        if name:
            queryset = queryset.filter(user__username__icontains=name)
        if account_number:
            queryset = queryset.filter(account_number=account_number)

        return queryset
    
class AccountDeleteView(generics.DestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAdminUser | IsStaffUser]


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

# -------------------------------------->Transactions<---------------------------------------------------------


class DepositFundsAPIView(APIView):
    def post(self, request):
        account_id = request.data.get('account_id')
        deposit_amount = request.data.get('deposit_amount')

        try:
            account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

        if deposit_amount <= 0:
            return Response({'error': 'Deposit amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            source_account = account
            if account.account_type == 'fixed_deposit':
                try:
                    fd_instance = FixedDepositAccount.objects.get(account=account)
                except FixedDepositAccount.DoesNotExist:
                    return Response({'error': 'Fixed deposit account not found'}, status=status.HTTP_404_NOT_FOUND)
                
               
                source_account_id = fd_instance.source_account_id
            elif account.account_type == 'recurring_deposit':
                try:
                    rd_instance = RecurringDepositAccount.objects.get(account=account)
                except RecurringDepositAccount.DoesNotExist:
                    return Response({'error': 'Recurring deposit account not found'}, status=status.HTTP_404_NOT_FOUND)
                
                source_account_id = rd_instance.source_account_id
            else:
                return Response({'error': 'Unsupported account type'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                source_account = Account.objects.get(id=source_account_id)
            except Account.DoesNotExist:
                return Response({'error': 'Source account not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if source_account.amount < deposit_amount:
                return Response({'error': 'Insufficient funds in the source account'}, status=status.HTTP_400_BAD_REQUEST)
            source_account.amount -= deposit_amount
            source_account.save()

            account.amount += deposit_amount
            account.save()

            transaction_log = Transaction.objects.create(
                user=request.user, 
                amount=deposit_amount,
                sender_id=source_account_id,
                receiver_id=account_id,
                description='Funds deposited into FD account'
            )

        return Response({'message': 'Deposit successful'}, status=status.HTTP_200_OK)


class WithdrawAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        account_id = request.data.get('account_id')

        try:
            account = Account.objects.select_for_update().get(id=account_id)
        except Account.DoesNotExist:
            return Response({"error": "Account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if account.account_type == 'recurring_deposit':
            try:
                recurring_deposit_account = RecurringDepositAccount.objects.get(account=account)
            except RecurringDepositAccount.DoesNotExist:
                return Response({"error": "Recurring deposit account not found"}, status=status.HTTP_404_NOT_FOUND)

            if recurring_deposit_account.years > 0 or recurring_deposit_account.months > 0:
                return Response({"error": "Duration not over for recurring deposit account"}, status=status.HTTP_400_BAD_REQUEST)

            initial_amount = recurring_deposit_account.initial_amount
            total_amount = initial_amount

            account.amount -= total_amount
            account.save()

            linked_account_id = recurring_deposit_account.source_account_id
            try:
                linked_account = Account.objects.select_for_update().get(id=linked_account_id)
            except Account.DoesNotExist:
                return Response({"error": "Linked account not found"}, status=status.HTTP_404_NOT_FOUND)
            
            linked_account.amount += total_amount
            linked_account.save()
            Transaction.objects.create(sender=account, receiver=linked_account, amount=total_amount, transaction_date=timezone.now(), description="Withdrawal from recurring deposit account", status="Completed")

            return Response({"message": "Withdrawal successful", "amount": total_amount}, status=status.HTTP_201_CREATED)
        
        elif account.account_type == 'fixed_deposit':
            try:
                fixed_deposit_account = FixedDepositAccount.objects.get(account=account)
            except FixedDepositAccount.DoesNotExist:
                return Response({"error": "Fixed deposit account not found"}, status=status.HTTP_404_NOT_FOUND)

            if fixed_deposit_account.years > 0 or fixed_deposit_account.months > 0:
                return Response({"error": "Duration not over for fixed deposit account"}, status=status.HTTP_400_BAD_REQUEST)

            initial_amount = fixed_deposit_account.intial_amount
            total_amount = initial_amount

            account.amount -= total_amount
            account.save()

            linked_account_id = fixed_deposit_account.source_account_id
            try:
                linked_account = Account.objects.select_for_update().get(id=linked_account_id)
            except Account.DoesNotExist:
                return Response({"error": "Linked account not found"}, status=status.HTTP_404_NOT_FOUND)
            
            linked_account.amount += total_amount
            linked_account.save()

            Transaction.objects.create(sender=account, receiver=linked_account, amount=total_amount, transaction_date=timezone.now(), description="Withdrawal from fixed deposit account", status="Completed",user=request.user)

            return Response({"message": "Withdrawal successful", "amount": total_amount}, status=status.HTTP_201_CREATED)
        
        else:
            return Response({"error": "Withdrawal not supported for this account type"}, status=status.HTTP_400_BAD_REQUEST)

class FundTransferAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        sender_account_id = request.data.get('sender')
        receiver_account_number = request.data.get('receiver')
        amount = request.data.get('amount')
        logged_in_user = request.user
        try:
            sender_account = Account.objects.select_for_update().get(id=sender_account_id, user=logged_in_user)
            receiver_account = Account.objects.select_for_update().get(account_number=receiver_account_number)
        except Account.DoesNotExist:
            return Response({"error": "Sender or receiver account does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if sender_account.account_type in ['fixed_deposit', 'recurring_deposit']:
            return Response({"error": "Cannot transfer funds"}, status=status.HTTP_400_BAD_REQUEST)
        if receiver_account.account_type in ['fixed_deposit', 'recurring_deposit']:
            return Response({"error": "Cannot transfer funds to fixed deposit or recurring deposit accounts"}, status=status.HTTP_400_BAD_REQUEST)
        
        account_info = AccountInfo.objects.first()  

        if sender_account.account_type == 'savings':
            today = date.today()
            today_transactions = Transaction.objects.filter(sender=sender_account, transaction_date__date=today)

            if today_transactions.count() >= account_info.transaction_limit:
                return Response({"error": "Transaction limit exceeded for today"}, status=status.HTTP_400_BAD_REQUEST)

            today_transactions_amount = today_transactions.aggregate(total_amount=Sum('amount'))['total_amount']
            if today_transactions_amount and (today_transactions_amount + amount) > account_info.max_transaction_amount:
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

        transaction_instance = Transaction.objects.create(sender=sender_account, receiver=receiver_account, amount=amount, user=logged_in_user)
        serializer = TransactionSerializer(transaction_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionListAPIView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = LimitOffsetPagination


class AccountBalanceAPIView(generics.RetrieveAPIView):
    serializer_class = AccountBalanceSerializer

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.account_type in ['savings', 'current']:
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            message = "Your account balance information is not available."
            return Response({'message': message}, status=status.HTTP_200_OK)
        

class DownloadAccountStatement(APIView):
    def get(self, request, account_id):
        authenticated_user = request.user
        try:
            account = Account.objects.get(id=account_id, user=authenticated_user)
        except Account.DoesNotExist:
            return Response({"detail": "Account does not exist or you are not authorized to access it."}, status=status.HTTP_404_NOT_FOUND)

        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                return HttpResponse("Invalid date format. Please use YYYY-MM-DD format.", status=400)

            transactions = Transaction.objects.filter(sender=account, transaction_date__range=(start_date, end_date))

            pdf_buffer = generate_account_statement_pdf(transactions)  

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="account_statement.pdf"'
            pdf_buffer.seek(0)
            response.write(pdf_buffer.getvalue())

            return response
        else:
            return HttpResponse("Please provide both start_date and end_date parameters.", status=400)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "You are successfully applied."}, status=status.HTTP_201_CREATED, headers=headers)

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


