from django.urls import path
from .views import *

urlpatterns = [
    path('account-info/', AccountInfoAPIView.as_view(), name='account-info-list'),
    path('account-info/<int:pk>/', AccountInfoDetailAPIView.as_view(), name='account-info-detail'),
]
