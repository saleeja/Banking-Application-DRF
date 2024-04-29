from django.db import models
from accounts.models import *

class Loan(models.Model):
    TYPE_CHOICES = (
        ('personal', 'Personal Loan'),
        ('home', 'Home Loan'),
        ('car', 'Car Loan'),
        ('education', 'Education Loan'),
    )
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    application_date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_date = models.DateTimeField(null=True, blank=True)
