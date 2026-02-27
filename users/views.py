from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer,RegisterResponseSerializer,LoginSerializer,LogoutSerializer,LoginResponseSerializer,ErrorResponseSerializer,UserSerializer
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
@extend_schema(
    tags=["Authentication"],
    summary="Register new user",
    description="Create new account using email, phone and password.",
    request=RegisterSerializer,
    responses={
        201: RegisterResponseSerializer,
        400: OpenApiResponse(description="Validation error"),
    },
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "email": "test@example.com",
                "phone": "01012345678",
                "password": "StrongPass123"
            },
            request_only=True,
        )
    ],
)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User created successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Authentication"],
    summary="User Login",
    description="Login using email and password to get JWT tokens.",
    request=LoginSerializer,
    responses={
        200: LoginResponseSerializer,
        401: OpenApiResponse(description="Invalid credentials"),
    },
)
class LoginView(APIView):
    def post(self, request):
        user = authenticate(
            email=request.data.get("email"),
            password=request.data.get("password")
        )

        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

@extend_schema(
    tags=["Authentication"],
    summary="Logout user",
    description="Blacklist refresh token.",
    request=LogoutSerializer,
    responses={
        205: OpenApiResponse(description="Successfully logged out"),
        400: OpenApiResponse(description="Refresh token required"),
    },
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out successfully"})
        except Exception:
            return Response({"error": "Invalid token"}, status=400)



@extend_schema(
    tags=["User"],
    summary="Get user profile",
    description="Retrieve authenticated user data.",
    responses={200: UserSerializer},
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = ProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)