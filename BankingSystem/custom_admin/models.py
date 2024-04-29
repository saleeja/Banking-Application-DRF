from django.db import models
from banking.models import *

class AccountInfo(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    fixed_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    recurring_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    transaction_limit = models.IntegerField(default=5)
    max_transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    min_deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)