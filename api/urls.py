from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from api.views import (
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    PasajeroListCreateView,
    RegistroCreateView,
    AeropuertoListCreateAPIView,
    AeropuertoDetailAPIView,
    VueloListCreateAPIView,
    # 👉 más vistas se irán sumando aquí (reservas, boletos, reportes…)
)

router = DefaultRouter()
# 👉 cuando tengas ViewSets (por ej. VuelosViewSet), los registramos:
# router.register('vuelos', VuelosViewSet, basename='vuelos')

urlpatterns = [
    # === Usuarios ===
    path('users/', UserListCreateView.as_view(), name='users-list'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='users-detail'),

    # === Pasajeros por usuario ===
    path('users/<int:user_pk>/pasajeros/', PasajeroListCreateView.as_view(), name='pasajeros-list'),

    # === Registro (usuario + pasajero) ===
    path('registro/', RegistroCreateView.as_view(), name='registro'),

    # === Aeropuertos ===
    path('aeropuertos/', AeropuertoListCreateAPIView.as_view(), name='aeropuertos-list'),
    path('aeropuertos/<int:pk>/', AeropuertoDetailAPIView.as_view(), name='aeropuerto-detail'),

    # === Vuelos ===
    path('vuelos/', VueloListCreateAPIView.as_view(), name='vuelos-list'),
    # Cuando agreguemos detalle/edición/borrado:
    # path('vuelos/<int:pk>/', VueloDetailAPIView.as_view(), name='vuelos-detail'),

    # === Documentación OpenAPI / Swagger ===
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # === Router para futuros ViewSets ===
    path('', include(router.urls)),
]
