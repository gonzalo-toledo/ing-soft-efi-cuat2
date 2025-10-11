import django
import os
import pytest
from django.conf import settings

#define la variable de entorno para que apunte al archivo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aerolinea.settings') 
django.setup()

#y despues importo
from rest_framework.test import APIClient

#fixture
@pytest.fixture
def api_client():
    return APIClient()
