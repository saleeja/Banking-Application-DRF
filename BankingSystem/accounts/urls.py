from django.urls import path
from .views import *


urlpatterns = [
# ---------------------------Authentication-----------------------------------------
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('validate-otp/', EmailVerificationView.as_view(), name='otp_validation'),
    path('staff/approval/', StaffApprovalView.as_view(), name='staff_approval'),
    path('users/', UserProfileListView.as_view(), name='user_profile_list'),
    path('staff/profiles/', StaffProfileListView.as_view(), name='user_profile_list'),
    path('users/<int:pk>/', UserProfileDeleteView.as_view(), name='user_profile_delete'),
    path('profiles/details/', UserUpdateDetail.as_view(), name='user-profile-details'),
    path('profiles/update/', UserUpdateDetail.as_view(), name='user-profile-update'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
# ---------------------------------Budgets-----------------------------------------
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('budgets/create/', BudgetCreateAPIView.as_view(), name='budget-create'),
    path('budgets/<int:pk>/', BudgetRetrieveUpdateDestroyAPIView.as_view(), name='budget-retrieve-update-destroy'),
# ---------------------------------Goals---------------------------------------------
    path('goals/create/', GoalCreateView.as_view(), name='savings-goal-create'),
    path('goals/list/', GoalListView.as_view(), name='savings-goal-list'),
    path('goals/<int:pk>/update/', GoalUpdateView.as_view(), name='goal-update'),
    path('goals/<int:pk>/delete/', GoalDeleteView.as_view(), name='goal-delete'),
]