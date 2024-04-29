from django.urls import path
from .views import *



urlpatterns = [
    
    path('create/', CreateAccountAPIView.as_view(), name='create-account'),
    path('opened-accounts/', OpenedAccountListAPIView.as_view(), name='opened-account-list'),
    path('account/balance/', AccountBalanceAPIView.as_view(), name='account_balance'),
    path('accounts/<int:pk>/balance/', AccountBalanceAPIView.as_view(), name='account-balance'),
    path('accounts/deposit/', DepositFundsAPIView.as_view(), name='deposit_funds'),
    path('accounts/withdraw/', WithdrawAPIView.as_view(), name='withdraw_funds'),
    path('accounts/transfer/', FundTransferAPIView.as_view(), name='fund_transfer'),
    path('transactions/', TransactionListAPIView.as_view(), name='transaction-list'),
]

