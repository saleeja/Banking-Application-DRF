from django.contrib import admin
from .models import Account, CurrentAccount,SavingAccount,RecurringDepositAccount,FixedDepositAccount

admin.site.register(Account)
admin.site.register(SavingAccount)
admin.site.register(CurrentAccount)
admin.site.register(RecurringDepositAccount)
admin.site.register(FixedDepositAccount)