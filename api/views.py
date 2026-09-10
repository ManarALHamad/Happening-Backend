from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile

from .serializers import UserSerializer


# create the jwt token 

def create_access_token(user):
    token = RefreshToken.for_user(user).access_token
    token["payload"] = {
        "_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "user_type": user.profile.user_type,

    }
    return str(token)

#SignUp post method 

@api_view(["POST"])
@permission_classes([AllowAny])
def sign_up(request):

    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")
    confirm_password = request.data.get("confirmPassword", "")
    user_type = request.data.get("user_type", "User")

    if not username or not password:
        return Response(
            {"err": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if password != confirm_password:
        return Response(
            {"err": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_type not in ("Founder", "User"):
        return Response(
            {"err":"Invalid user type"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if User.objects.filter(username=username).exists():
        return Response(
            {"err": "That username already taken"},
            status=status.HTTP_400_BAD_REQUEST,

        )
    if User.objects.filter(email=email).exists():
         return Response(
            {"err": "this email is already registered"},
            status=status.HTTP_400_BAD_REQUEST,
        
       )

    