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
    path('account-info/', AccountInfoAPIView.as_view(), name='account-info-list'),
    path('account-info/<int:pk>/', AccountInfoDetailAPIView.as_view(), name='account-info-detail'),
# ----------------------------------------->LOAN<-----------------------------------------------------------------------
    path('loan/types/', LoanTypeCreate.as_view(), name='loan-type-list'),
    path('loan/create/', LoanApplicationCreate.as_view(), name='loan-application-list'),
    path('myloan/', UserLoanApplicationList.as_view(), name='user-loan-application-list'),
    path('my-loan-applications/<int:pk>/', UserLoanApplicationDetail.as_view(), name='user-loan-application-detail'),
    path('loan/applications/<int:pk>/approval/', LoanApplicationApproval.as_view(), name='loan-application-approval'),
    path('loan/list/', LoanApplicationList.as_view(), name='loan-application-list'),

]

