from django.db import models
from accounts.models import UserProfile
from django.core.exceptions import ValidationError
from accounts.models import Budget
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F,Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db import models
from banking.models import *


class Account(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SavingAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    Purpose = models.CharField(max_length=255)


class CurrentAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    nature_of_business = models.CharField(max_length=255)
    business_category = models.CharField(max_length=100)
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


class AccountInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    fixed_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    recurring_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    transaction_limit = models.IntegerField(default=5)
    max_transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    min_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Transaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    sender = models.ForeignKey(Account, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Transaction)
def check_transaction_budget(sender, instance, created, **kwargs):
    if created:
        # Check if the receiver has a CurrentAccount
        current_account = CurrentAccount.objects.filter(account=instance.receiver).first()
        if current_account:
            # Retrieve the budget for the business category
            budget = Budget.objects.filter(user=instance.user, category__name=current_account.business_category).first()
            if budget and instance.amount > budget.total_budget:
                # Send email alert
                subject = f"Budget Exceeded for {current_account.business_category}"
                message = f"You have exceeded your budget for {current_account.business_category}. Total spent: {instance.amount}, Budget: {budget.total_budget}"
                send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.user.email], fail_silently=False)
    

class LoanType(models.Model):
    name = models.CharField(max_length=100)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  


class LoanApplication(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    approved_date = models.DateTimeField(auto_now=True)