from rest_framework import serializers
from .models import *


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['account_number','user']


class SavingsAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingAccount
        exclude = ['account']


class CurrentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentAccount
        exclude = ['account']


class FixedDepositAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedDepositAccount
        exclude = ['account','source_account_id','deposit_amount']

    def validate_duration_months(self, value):
        
        min_duration = 7
        max_duration = 10 * 12 * 30  
        
        if value < min_duration or value > max_duration:
            raise serializers.ValidationError("Duration must be between 7 days and 10 years.Please contact the bank for assistance.")

        return value

    def validate_deposit_amount(self, value):
        if value < 1000:
            raise serializers.ValidationError("Deposit amount must be 1000 or more for fixed deposit accounts.")
        return value


class RecurringDepositAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringDepositAccount
        exclude = ['account','source_account_id']

    def validate_intial_amount(self, value):
        if value < 100:
            raise serializers.ValidationError("Minimum deposit amount for recurring deposit accounts is Rs. 100 per month.")
        return value
    
    def validate_duration_months(self, value):
        min_duration = 6
        max_duration = 120  
        if value < min_duration or value > max_duration:
            raise serializers.ValidationError("Duration for recurring deposit accounts must be between 6 months and 10 years (120 months).")
        return value


class AccountBalanceSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    message = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['account_number', 'account_type', 'amount', 'message']

    def get_message(self, instance):
        return f"Your balance for {instance.account_type} account is Rs. {instance.amount}"


class AllAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_number', 'account_type']


class AccountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountInfo
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['sender', 'receiver', 'amount', 'transaction_date']


class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

# -----------------------------------------------------------------------------------------------

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['loan_type','amount','monthly_income']

    def validate_amount(self, value):
        min_amount = 15000
        max_amount = 10000000

        if value < min_amount:
            raise serializers.ValidationError("The maximum loan amount you can apply for is 15,000.")
        elif value > max_amount:
            raise serializers.ValidationError("The loan amount must not exceed ₹1 crore.")

        return value
   
        
class LoanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanType
        fields = '__all__'


class LoanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'



