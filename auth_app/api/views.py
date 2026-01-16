from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

from .serializers import RegistrationSerializer, LoginTokenObtainPairSerializer, PasswordResetSerializer, PasswordConfirmSerializer
from auth_app.signals import user_registered, password_reset
from .permissions import IsOwner


class RegistrationView(APIView):
    """
    Handle user registration requests.
    Creates an inactive user and triggers the activation email signal.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validate input data, create a user, and return registration details.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            token = default_token_generator.make_token(user)

            user_registered.send(
                sender=self.__class__,
                user=user,
                token=token
            )

            return Response(
                {
                    'user': {
                        'id':user.id,
                        'email':user.email
                    },
                    'token':token
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    """
    Activate a user account using a UID and token.
    Validates the activation link and enables the account.
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token, *args, **kwargs):
        """
        Verify activation token and activate the corresponding user.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True 
                user.save()
                return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Activation link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Authenticate a user and issue JWT tokens via HTTP-only cookies.
    Uses email/password validation before token generation.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validate credentials and set access/refresh tokens as cookies.
        """
        serializer = LoginTokenObtainPairSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response(
            {
                "detail": "Login successfully!",
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        return response
    

class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh the JWT access token using a refresh token from cookies.
    Issues a new access token if the refresh token is valid.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Validate refresh token and update the access token cookie.
        """
        refresh = request.COOKIES.get("refresh_token")

        if refresh is None:
            return Response(
                {'detail': 'Refresh token not found!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data={'refresh':refresh})

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {'detail': 'Refresh token invalid!'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = serializer.validated_data.get("access")

        response = Response(
            {
                'detail': 'Token refreshed',
                'access': access_token
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response
    

class LogoutView(APIView):
    """
    Log out the current user.
    Blacklists the refresh token and clears authentication cookies.
    """
    permission_classes = [IsOwner]

    def post(self, request):
        """
        Invalidate refresh token and remove access/refresh cookies.
        """
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            print(f"Failed to move the token to the blacklist: {e}")

        response = Response(
            {
                "detail": (
                    "Log-Out successfully! All Tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
    

class PasswordResetView(APIView):
    """
    Initiate a password reset process.
    Sends a password reset email if the user exists.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validate email and trigger the password reset signal.
        """
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        self._handle_password_reset_request(serializer.validated_data['email'])

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )

    def _handle_password_reset_request(self, email):
        """
        Generate a reset token and send the password reset signal.
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        token = default_token_generator.make_token(user)

        password_reset.send(
            sender=self.__class__,
            user=user,
            token=token
        )
        

class PasswordResetConfirmView(APIView):
    """
    Confirm a password reset using UID and token.
    Sets a new password after successful validation.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """
        Validate reset data, token, and update the user password.
        """
        serializer = PasswordConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = self._get_user(uidb64)

        error_response = self._validate_token(user, token)
        if error_response:
            return error_response

        self._set_new_password(user, serializer.validated_data['new_password'])

        return Response(
            {"detail": "Your password has been successfully reset."},
            status=status.HTTP_200_OK
        )

    def _get_user(self, uidb64):
        """
        Decode UID and return the associated user or None.
        """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            return User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def _validate_token(self, user, token):
        """
        Ensure the reset token is valid for the given user.
        """
        if user is None:
            return Response(
                {"error": "Invalid reset link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return None

    def _set_new_password(self, user, new_password):
        """
        Update and persist the user's new password.
        """
        user.set_password(new_password)
        user.save()