from django.urls import path
from .views import *



urlpatterns = [
#-------------------------------->Account Management<--------------------------------------------------
    path('accounts/create/', CreateAccountAPIView.as_view(), name='create-account'),
    path('accounts/opened/', OpenedAccountListAPIView.as_view(), name='opened-account-list'),
    path('account/balance/', AccountBalanceAPIView.as_view(), name='account_balance'),
    path('account/info/', AccountInfoAPIView.as_view(), name='account-info-list'),
    path('account/info/<int:pk>/', AccountInfoDetailAPIView.as_view(), name='account-info-detail'),
    path('account/info/<int:pk>/delete/', AccountInfoDeleteView.as_view(), name='account_info_delete'),
    path('auth/accounts/', AuthAccountListView.as_view(), name='account-list'),
    path('auth/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),

#---------------------------------->Transactions<-------------------------------------------------------
    path('accounts/deposit/', DepositFundsAPIView.as_view(), name='deposit_funds'),
    path('deposit/<int:pk>/', DepositFundsAPIView.as_view(), name='fixed-deposit-deposit'),
    path('accounts/withdraw/', WithdrawAPIView.as_view(), name='withdraw_funds'),
    path('accounts/transfer/', FundTransferAPIView.as_view(), name='fund_transfer'),
    path('accounts/transactions/', TransactionListAPIView.as_view(), name='transaction-list'),
    path('accounts/<int:pk>/balance/', AccountBalanceAPIView.as_view(), name='account-balance'),
    path('download/account/statement/<int:account_id>/', DownloadAccountStatement.as_view(), name='download_account_statement'),

#----------------------------------------->LOAN<---------------------------------------------------------
    path('loan/types/', LoanTypeCreate.as_view(), name='loan-type-list'),
    path('loan/create/', LoanApplicationCreate.as_view(), name='loan-application-list'),
    path('myloan/', UserLoanApplicationList.as_view(), name='user-loan-application-list'),
    path('myloan/applications/<int:pk>/', UserLoanApplicationDetail.as_view(), name='user-loan-application-detail'),
    path('loan/applications/<int:pk>/approval/', LoanApplicationApproval.as_view(), name='loan-application-approval'),
    path('loan/list/', LoanApplicationList.as_view(), name='loan-application-list'),

]

