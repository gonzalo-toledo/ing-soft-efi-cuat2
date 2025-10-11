from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from api.views import (
    AeropuertoDetailAPIView,
    AeropuertoListCreateAPIView,
    BoletoDetailAPIView,
    BoletoListCreateAPIView,
    DestinosPopularesAPIView,
    EstadisticasGeneralesAPIView,
    OcupacionVuelosAPIView,
    PasajeroListCreateView,
    RegistroCreateView,
    ReservaDetailAPIView,
    ReservaListCreateAPIView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    VueloViewSet,
)

router = DefaultRouter()
router.register('vuelos', VueloViewSet, basename='vuelos')

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
    # path('vuelos/', VueloListCreateAPIView.as_view(), name='vuelos-list'),

    # === Reservas y Boletos (ViewSets) ===
    path('reservas/', ReservaListCreateAPIView.as_view(), name='reservas-list'),
    path('reservas/<int:pk>/', ReservaDetailAPIView.as_view(), name='reserva-detail'),
    path('boletos/', BoletoListCreateAPIView.as_view(), name='boletos-list'),
    path('boletos/<int:pk>/', BoletoDetailAPIView.as_view(), name='boleto-detail'),
    
    # === Estadísticas ===
    path('estadisticas/general/', EstadisticasGeneralesAPIView.as_view(), name='estadisticas-general'),
    path('estadisticas/vuelos_ocupacion/', OcupacionVuelosAPIView.as_view(), name='estadisticas-vuelos-ocupacion'),
    path('estadisticas/destinos_populares/', DestinosPopularesAPIView.as_view(), name='estadisticas-destinos-populares'),
    
    # === Documentación OpenAPI / Swagger ===
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # === Router para futuros ViewSets ===
    path('', include(router.urls)),
]
