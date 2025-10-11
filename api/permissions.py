from django.conf import settings
from rest_framework.permissions import BasePermission


VALID_TOKENS = [
    "token-valido-123",
    "7777"
]

class TokenPermission(BasePermission):
    """
    Permiso basado en un header Authorization: Bearer <token>
    """
    message = 'Token de autenticación inválido'
    
    def has_permission(self, request, view):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split(' ')[1].strip()
        return token in VALID_TOKENS