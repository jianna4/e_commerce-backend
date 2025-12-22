from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from .models import User

# 1️⃣ Register
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {"message": "User registered", "user": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2️⃣ Login
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    initials = "".join([p[0].upper() for p in user.full_name.strip().split()[:2]]) if user.full_name else user.email[0].upper()

    return Response({
        "message": "Login successful",
        "user": {"email": user.email, "full_name": user.full_name, "initials": initials},
        "tokens": {"refresh": str(refresh), "access": str(refresh.access_token)}
    })


# 3️⃣ Me endpoint
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    initials = "".join([p[0].upper() for p in user.full_name.strip().split()[:2]]) if user.full_name else user.email[0].upper()
    return Response({"email": user.email, "full_name": user.full_name, "initials": initials})
