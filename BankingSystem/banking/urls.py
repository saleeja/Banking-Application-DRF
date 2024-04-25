from django.urls import path
from .views import *


urlpatterns = [
    path('account/create/', AccountCreateAPIView.as_view(), name='account-create'),
    path('accounts/balance/<int:pk>/', AccountDetailAPIView.as_view(), name='account-detail'),
    path('accounts/deposit/', DepositFundsAPIView.as_view(), name='deposit_funds'),
    path('accounts/withdraw/', WithdrawFundsAPIView.as_view(), name='withdraw_funds'),
    path('accounts/transfer/', FundTransferAPIView.as_view(), name='fund_transfer'),
    path('transactions/', TransactionListAPIView.as_view(), name='transaction-list'),
]

