from django.urls import path
from .views import *


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('validate-otp/', EmailVerificationView.as_view(), name='otp_validation'),
    path('users/', UserProfileListView.as_view(), name='user_profile_list'),
    path('users/<int:pk>/', UserProfileDeleteView.as_view(), name='user_profile_delete'),
    path('profiles/details/', UserUpdateDetail.as_view(), name='user-profile-details'),
    path('profiles/update/', UserUpdateDetail.as_view(), name='user-profile-update'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('budgets/create/', BudgetCreateAPIView.as_view(), name='budget-create'),

    
]