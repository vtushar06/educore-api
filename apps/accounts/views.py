from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserProfileSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/

    Create a new user account. Role defaults to 'student' if not specified.
    Admin role cannot be self-assigned.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "detail": "Account created successfully.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT /api/v1/auth/profile/

    Retrieve or update the authenticated user's profile.
    """

    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
