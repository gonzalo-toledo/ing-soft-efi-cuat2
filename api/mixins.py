#Un mixin es una clase que contiene metodos que se pueden heredar en otras clases
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class AuthViewMixin:
    """
    clase base para vistas que requieren autenticación
    """
    permission_classes = [IsAuthenticated]
    

class AuthAdminViewMixin:
    """
    clase base para vistas que requieren autenticación de admin
    """
    permission_classes = [IsAdminUser]