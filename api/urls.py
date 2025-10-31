from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from api.views import (
    AvionDetailAPIView,
    AvionListCreateAPIView,
    AsientoListAPIView,
    AeropuertoDetailAPIView,
    AeropuertoListCreateAPIView,
    BoletoDetailAPIView,
    BoletoListCreateAPIView,
    DestinosPopularesAPIView,
    EstadisticasGeneralesAPIView,
    OcupacionVuelosAPIView,
    PasajeroDetailView,
    PasajeroListCreateView,
    PasajeroReservasView,
    RegistroCreateView,
    ReservaDetailAPIView,
    ReservaListCreateAPIView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    VueloListCreateAPIView,
    VueloDetailAPIView,
    ReservaAdminListAPIView
    
)

urlpatterns = [
    # === Usuarios ===
    path('users/', UserListCreateView.as_view(), name='users-list'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='users-detail'),

    # === Pasajeros por usuario ===
    path('users/<int:user_pk>/pasajeros/', PasajeroListCreateView.as_view(), name='pasajeros-list'),
    
    #=== Detalle pasajero ===
    path('users/<int:user_pk>/pasajeros/<int:pk>/', PasajeroDetailView.as_view(), name='pasajero-detail'),
    path('users/<int:user_pk>/pasajeros/<int:pk>/reservas/', PasajeroReservasView.as_view(), name='pasajero-reservas'),

    # === Registro (usuario + pasajero) ===
    path('registro/', RegistroCreateView.as_view(), name='registro'),

    # === Aeropuertos ===
    path('aeropuertos/', AeropuertoListCreateAPIView.as_view(), name='aeropuertos-list'),
    path('aeropuertos/<int:pk>/', AeropuertoDetailAPIView.as_view(), name='aeropuerto-detail'),

    # === Aviones y Asientos ===
    path("aviones/", AvionListCreateAPIView.as_view(), name="avion-list"),
    path("aviones/<int:pk>/", AvionDetailAPIView.as_view(), name="avion-detail"),
    path("aviones/<int:avion_id>/asientos/", AsientoListAPIView.as_view(), name="avion-asientos"),
    path("asientos/", AsientoListAPIView.as_view(), name="asiento-list"),

    # === Vuelos ===
    path('vuelos/', VueloListCreateAPIView.as_view(), name='vuelos-list'),
    path('vuelos/<int:pk>/', VueloDetailAPIView.as_view(), name='vuelo-detail'),

    # === Reservas y Boletos ===
    path('reservas/', ReservaListCreateAPIView.as_view(), name='reservas-list'),
    path("reservas/<int:pk>/estado/", ReservaDetailAPIView.as_view(), name="reserva-estado"),
    path('admin/reservas/', ReservaAdminListAPIView.as_view(), name='admin-reservas-list'),
    # path('reservas/<int:pk>/', ReservaDetailAPIView.as_view(), name='reserva-detail'),
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
]
