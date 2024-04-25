from django.urls import path
from .views import *


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('validate-otp/', EmailVerificationView.as_view(), name='otp_validation'),
    path('users/', UserProfileListView.as_view(), name='user_profile_list'),
    path('users/<int:pk>/', UserProfileDeleteView.as_view(), name='user_profile_delete'),
    path('profiles/', UserUpdateDetail.as_view(), name='user-profile-create'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
]