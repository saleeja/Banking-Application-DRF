from django.db import models
from accounts.models import UserProfile
import random

class Account(models.Model):
    TRANSACTION_LIMIT = 5
    ACCOUNT_TYPES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
        ('fixed_deposit', 'Fixed Deposit'),
        ('recurring_deposit', 'Recurring Deposit'),
    ]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=12, unique=True,blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    transaction_limit = models.PositiveIntegerField(default=TRANSACTION_LIMIT)
    transactions_made = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SavingAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    Purpose = models.CharField(max_length=255)


class CurrentAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    nature_of_business = models.CharField(max_length=255)
    business_address = models.TextField()
    business_phone_number = models.CharField(max_length=20)
    business_email_address = models.EmailField()

   
class RecurringDepositAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='recurring_deposit_account')
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    duration_months = models.PositiveIntegerField() 
    source_account_id = models.PositiveIntegerField()
    intial_amount =models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Recurring Account: {self.account.account_number}"


class FixedDepositAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='fixed_deposit_account')
    duration_months = models.PositiveIntegerField()  
    deposit_amount=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    source_account_id = models.PositiveIntegerField()
    

    def __str__(self):
        return f"Fixed Deposit Account: {self.account.account_number}"


class Transaction(models.Model):
    sender = models.ForeignKey(Account, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)