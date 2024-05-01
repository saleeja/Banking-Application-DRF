from rest_framework import generics,status
from rest_framework.response import Response
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny,IsAdminUser
from django.utils import timezone
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from .serializers import *
from .models import *
import random
import string
from .permissions import IsStaffUser


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def generate_otp(self, length=6):
        """Generate a random OTP of specified length."""
        otp = ''.join(random.choices(string.digits, k=length))
        return otp

    def send_otp_email(self, email, otp):
        """Send OTP to the user's email."""
        subject = 'Your OTP for login'
        message = f'Your OTP for login is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, [email])

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Check if the registration is for staff
            is_staff = serializer.validated_data.get('is_staff', False)
            # Generate OTP and send email
            otp = self.generate_otp() 
            self.send_otp_email(serializer.validated_data['email'], otp)

            # Save OTP to session
            request.session['otp'] = otp
            request.session['user_data'] = serializer.validated_data

        
            return Response({"message": "OTP sent for registration. Please verify your email to complete registration."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        otp = request.session.get('otp')
        user_data = request.session.get('user_data')
        if otp and user_data:
            # Validate OTP
            if request.data.get('otp') == otp:
                serializer = self.serializer_class(data=user_data)
                if serializer.is_valid():
                    user = serializer.save(otp_verified=True)
                    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "OTP not found"}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_staff and not user.is_approved and not user.is_superuser:
                    return Response({"detail": "Staff account requires admin approval. Please wait for approval."}, status=status.HTTP_403_FORBIDDEN)
                user.last_login = timezone.now()
                user.save()     
                # Generate access token
                access_token = AccessToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'access': str(access_token),
                })
            else:
                return Response({'detail': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffApprovalView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.filter(is_staff=True, is_approved=False)
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):
        staff_id = request.data.get('staff_id')
        action = request.data.get('action') 
        
        staff_account = self.get_object(staff_id)
        if staff_account:
            if action == 'approve':
                staff_account.is_approved = True
                staff_account.save()
                return Response({"message": "Staff account approved successfully."}, status=status.HTTP_200_OK)
            elif action == 'reject':
                staff_account.delete()  
                return Response({"message": "Staff account rejected successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Staff account not found or already approved."}, status=status.HTTP_404_NOT_FOUND)

    def get_object(self, staff_id):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=staff_id)
            self.check_object_permissions(self.request, obj)
            return obj
        except UserProfile.DoesNotExist:
            return None


class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser | IsStaffUser]


class UserProfileDeleteView(generics.DestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser | IsStaffUser]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class UserUpdateDetail(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()


class LogoutAPIView(APIView):
    def post(self, request):
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


# from rest_framework_simplejwt.authentication import JWTAuthentication

# class UserLogoutAPIView(APIView):
  
#     authentication_classes = [JWTAuthentication]

#     def post(self, request, *args, **kwargs):
#         try:
#             # Blacklist the currently used access token
#             token = request.auth
#             if token:
#                 token.blacklist()
#                 return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"detail": "No token provided."}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"detail": "Failed to logout."}, status=status.HTTP_400_BAD_REQUEST)


class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class BudgetCreateAPIView(generics.CreateAPIView):
    serializer_class = BudgetSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer


class GoalListCreateAPIView(generics.ListCreateAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GoalRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

