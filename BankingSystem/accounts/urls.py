from django.urls import path
from .views import *


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('validate-otp/', EmailVerificationView.as_view(), name='otp_validation'),
    path('staff/approval/', StaffApprovalView.as_view(), name='staff_approval'),
    path('users/', UserProfileListView.as_view(), name='user_profile_list'),
    path('users/<int:pk>/', UserProfileDeleteView.as_view(), name='user_profile_delete'),
    path('profiles/details/', UserUpdateDetail.as_view(), name='user-profile-details'),
    path('profiles/update/', UserUpdateDetail.as_view(), name='user-profile-update'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('budgets/create/', BudgetCreateAPIView.as_view(), name='budget-create'),
    path('budgets/<int:pk>/', BudgetRetrieveUpdateDestroyAPIView.as_view(), name='budget-retrieve-update-destroy'),

    path('goals/', GoalListCreateAPIView.as_view(), name='goal-list-create'),
    path('goals/<int:pk>/', GoalRetrieveUpdateDestroyAPIView.as_view(), name='goal-detail'),
]