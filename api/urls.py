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
    VueloRetrieveUpdateDestroyAPIView,
    ReservaAdminListAPIView,
    BoletoAdminListApiView,
    BoletoListApiView,
    BoletoPorCodiogoAPIView,
    AsientoDisponibilidadAPIView,
    PasajeroReservasConfirmadasView,
    PasajeroReservasPendientesView,
    PasajerosPorVueloAPIView,
    
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
    path('users/<int:user_pk>/pasajeros/<int:pk>/reservas/confirmadas/', PasajeroReservasConfirmadasView.as_view(), name='pasajero-reservas-confirmadas'),
    path('users/<int:user_pk>/pasajeros/<int:pk>/reservas/pendientes/', PasajeroReservasPendientesView.as_view(), name='pasajero-reservas-pendientes'),

    # === Registro (usuario + pasajero) ===
    path('registro/', RegistroCreateView.as_view(), name='registro'),

    # === Aeropuertos ===
    path('aeropuertos/', AeropuertoListCreateAPIView.as_view(), name='aeropuertos-list'),
    path('aeropuertos/<int:pk>/', AeropuertoDetailAPIView.as_view(), name='aeropuerto-detail'),

    # === Aviones ===
    path("aviones/", AvionListCreateAPIView.as_view(), name="avion-list"),
    path("aviones/<int:pk>/", AvionDetailAPIView.as_view(), name="avion-detail"),
    path("aviones/<int:avion_id>/asientos/", AsientoListAPIView.as_view(), name="avion-asientos"),
    

    # === Vuelos ===
    path('vuelos/', VueloListCreateAPIView.as_view(), name='vuelos-list'),
    path('vuelos/<int:pk>/', VueloRetrieveUpdateDestroyAPIView.as_view(), name='vuelo-detail'),
    
    # === Asientos ===
    path("asientos/", AsientoListAPIView.as_view(), name="asiento-list"),
    path("vuelos/<int:vuelo_id>/asientos/<int:asiento_id>/disponibilidad/", AsientoDisponibilidadAPIView.as_view(), name="asiento-disponibilidad"),

    # === Reservas y Boletos ===
    path('reservas/', ReservaListCreateAPIView.as_view(), name='reservas-list'),
    path("reservas/<int:pk>/estado/", ReservaDetailAPIView.as_view(), name="reserva-estado"),
    path('admin/reservas/', ReservaAdminListAPIView.as_view(), name='admin-reservas-list'),
    path('boletos/', BoletoListApiView.as_view(), name='boletos-list'),
    path('admin/boletos/', BoletoAdminListApiView.as_view(), name='admin-boletos-list'),
    path('boletos/codigo/<str:codigo_barra>/', BoletoPorCodiogoAPIView.as_view(), name='boleto-por-codigo'),

    # === Estadísticas ===
    path("estadisticas/vuelos/<int:vuelo_id>/pasajeros/", PasajerosPorVueloAPIView.as_view(), name="vuelos-pasajeros"),
    path('estadisticas/general/', EstadisticasGeneralesAPIView.as_view(), name='estadisticas-general'),
    path('estadisticas/vuelos_ocupacion/', OcupacionVuelosAPIView.as_view(), name='estadisticas-vuelos-ocupacion'),
    path('estadisticas/destinos_populares/', DestinosPopularesAPIView.as_view(), name='estadisticas-destinos-populares'),

    # === Documentación OpenAPI / Swagger ===
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
