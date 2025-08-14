from django.contrib.auth.models import User
from rest_framework.generics import (
    ListAPIView, 
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView
)

from api.serializers import UserSerializer

class UserListCreateView(ListCreateAPIView):
    """
    GET /api/users/
        return -> [UserSerializer]
    POST /api/users/ -> crea un usuario
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    GET /api/users/{pk}/
        return -> UserSerializer
    PUT /api/users/{pk}/ -> actualiza un usuario
    PATCH /api/users/{pk}/ -> actualiza parcialmente un usuario
    DELETE /api/users/{pk}/ -> elimina un usuario
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer