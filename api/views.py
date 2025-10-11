from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)  # Se usa con permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from api.mixins import (
    AuthAdminViewMixin,
    AuthViewMixin,
)  # permite que le pasemos el permiso como una vista y no como un permission_class (herencia de clase)
from api.serializers import (
    AeropuertoSerializer,
    BoletoSerializer,
    DestinoPopularSerializer,
    EstadisticasGeneralesSerializer,
    OcupacionVueloSerializer,
    PasajeroSerializer,
    RegistroSerializer,
    ReservaSerializer,
    UserSerializer,
    VueloModelSerializer,
)
from pasajeros.models import Pasajero
from reservas.models import Boleto, Reserva
from vuelos.models import Aeropuerto, Vuelo
from aviones.models import Asiento 

# USERS

# class UserListView(ListAPIView):
#     '''
#     GET /api/users/
#       return -> [<UserSerializer>, ...]
#     '''
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class UserListCreateView(ListCreateAPIView):
    """
    GET /api/users/
        return -> [<UserSerializer>, ...]
    POST /api/users/ - crea un nuevo usuario
    """

    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    GET /api/users/
        return -> [<UserSerializer>, ...]
    PUT /api/users/1/ -> actualiza el usuario 1
    PATCH /api/users/1/ -> actualiza parcialmente el usuario 1
    DELETE /api/users/1/ -> elimina el usuario 1
    """

    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_destroy(self, instance):
        if instance.is_active:
            instance.is_active = False
            instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        return Response(
            {"detail": "Usuario desactivado correctamente."}, status=status.HTTP_200_OK
        )


# PASAJEROS
class PasajeroListCreateView(ListCreateAPIView, AuthViewMixin):
    """
    GET /api/users/<user_pk>/pasajeros/ -> lista pasajeros del usuario
    POST /api/users/<user_pk>/pasajeros/ -> crea pasajero para el usuario
    """

    serializer_class = PasajeroSerializer

    # redefino el queryset para filtrar por usuario:
    def get_queryset(self):
        user_pk = self.kwargs["user_pk"]
        return Pasajero.objects.filter(usuario_id=user_pk)

    def perform_create(self, serializer):
        user_pk = self.kwargs["user_pk"]  # obtengo el user_pk de la URL
        usuario = get_object_or_404(User, pk=user_pk)
        serializer.save(usuario=usuario)


# USUARIO + PASAJERO
class RegistroCreateView(CreateAPIView):
    """
    POST /api/registro/ -> crea un nuevo usuario + pasajero
    """

    queryset = Pasajero.objects.all()
    serializer_class = RegistroSerializer


# AEROPUERTOS (con APIView)
class AeropuertoListCreateAPIView(
    APIView, AuthAdminViewMixin
):  # con APIViewtengo que definir get y post
    """
    GET /api/aeropuertos/ -> lista todos los aeropuertos
    POST /api/aeropuertos/ -> crea un nuevo aeropuerto
    """

    def get(self, request):
        qs = Aeropuerto.objects.all().order_by("id")
        serializer = AeropuertoSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AeropuertoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                AeropuertoSerializer(instance).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AeropuertoDetailAPIView(APIView, AuthAdminViewMixin):
    """
    GET /api/vuelos/<id>/ -> detalle de un aeropuerto
    PUT /api/vuelos/<id>/ -> actualiza un aeropuerto
    PATCH /api/vuelos/<id>/ -> actualiza parcialmente un aeropuerto
    DELETE /api/vuelos/<id>/ -> elimina un aeropuerto
    """

    def get_object(self, pk):
        return get_object_or_404(Aeropuerto, pk=pk)

    def get(self, request, pk):
        instance = self.get_object(pk)
        return Response(AeropuertoSerializer(instance).data)

    def put(self, request, pk):
        instance = self.get_object(pk)
        serializer = AeropuertoSerializer(instance, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(AeropuertoSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        instance = self.get_object(pk)
        serializer = AeropuertoSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(AeropuertoSerializer(instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        instance = self.get_object(pk)
        instance.delete()
        return Response(
            {"detail": "Aeropuerto eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT,
        )


# VUELOS (con APIView)
# class VueloListCreateAPIView(APIView):
#     """
#     GET /api/vuelos/ -> lista todos los vuelos
#     POST /api/vuelos/ -> crea un nuevo vuelo
#     """
#     permission_classes = [TokenPermission]
#     def get(self, request):
#         qs = Vuelo.objects.all().order_by('id')
#         serializer = VueloSerializer(qs, many=True)
#         return Response(serializer.data)


class VueloViewSet(viewsets.ModelViewSet):
    """
    API REST completa para gestión de vuelos.
    Soporta:
    - GET /api/vuelos/ -> listar vuelos
    - GET /api/vuelos/{id}/ -> detalle
    - POST /api/vuelos/ -> crear vuelo (solo admin)
    - PUT/PATCH /api/vuelos/{id}/ -> actualizar vuelo (solo admin)
    - DELETE /api/vuelos/{id}/ -> eliminar vuelo (solo admin)
    Filtrable por ?origen=EZE&destino=MAD&fecha=2025-11-10
    """

    queryset = (
        Vuelo.objects.select_related("avion", "origen", "destino").all().order_by("id")
    )
    serializer_class = VueloModelSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        origen = self.request.query_params.get("origen")
        destino = self.request.query_params.get("destino")
        fecha = self.request.query_params.get("fecha")

        if origen:
            queryset = queryset.filter(origen__iata__iexact=origen)
        if destino:
            queryset = queryset.filter(destino__iata__iexact=destino)
        if fecha:
            queryset = queryset.filter(fecha_salida__date=fecha)

        return queryset.order_by("fecha_salida")


# =====================================================
# RESERVAS
# =====================================================


class ReservaListCreateAPIView(ListCreateAPIView):
    """
    GET /api/reservas/ -> listar reservas
    POST /api/reservas/ -> crear una nueva reserva
    """

    queryset = (
        Reserva.objects.select_related("vuelo", "pasajero", "asiento")
        .all()
        .order_by("-fecha_reserva")
    )
    serializer_class = ReservaSerializer

    def perform_create(self, serializer):
        # Al crear una reserva, marcamos como activa y pendiente
        serializer.save(activa=True, estado="Pendiente")


class ReservaDetailAPIView(APIView):
    """
    GET /api/reservas/<id>/ -> detalle de una reserva
    UPDATE /api/reservas/<id>/ -> actualizar reserva
    DELETE /api/reservas/<id>/ -> eliminar reserva
    """

    def get(self, request, pk):
        reserva = get_object_or_404(
            Reserva.objects.select_related("vuelo", "pasajero", "asiento"), pk=pk
        )
        serializer = ReservaSerializer(reserva)
        return Response(serializer.data)
    
    def put(self, request, pk):
        reserva = get_object_or_404(
            Reserva.objects.select_related("vuelo", "pasajero", "asiento"), pk=pk
        )
        serializer = ReservaSerializer(reserva, data=request.data)
        if serializer.is_valid():
            reserva = serializer.save()
            return Response(ReservaSerializer(reserva).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        reserva = get_object_or_404(
            Reserva.objects.select_related("vuelo", "pasajero", "asiento"), pk=pk
        )
        reserva.delete()
        return Response(
            {"detail": "Reserva eliminada correctamente."},
            status=status.HTTP_204_NO_CONTENT,
        )


# =====================================================
# BOLETOS
# =====================================================


class BoletoListCreateAPIView(ListCreateAPIView):
    """
    GET /api/boletos/ -> listar boletos
    POST /api/boletos/ -> generar nuevo boleto desde reserva confirmada
    """

    queryset = (
        Boleto.objects.select_related("reserva", "reserva__vuelo")
        .all()
        .order_by("-fecha_emision")
    )
    serializer_class = BoletoSerializer


class BoletoDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    GET /api/boletos/<id>/ -> detalle de un boleto
    PUT /api/boletos/<id>/ -> actualizar boleto
    DELETE /api/boletos/<id>/ -> eliminar boleto
    """

    queryset = (
        Boleto.objects.select_related("reserva", "reserva__vuelo")
        .all()
        .order_by("-fecha_emision")
    )
    serializer_class = BoletoSerializer


#====================================================
# ESTADISTICAS GENERALES DE VUELOS
#====================================================

class EstadisticasGeneralesAPIView(APIView):
    """
    GET /api/estadisticas/general/
    Devuelve conteos generales del sistema.
    """
    def get(self, request):
        data = {
            "total_vuelos": Vuelo.objects.count(),
            "total_pasajeros": Pasajero.objects.count(),
            "total_reservas": Reserva.objects.count(),
            "total_boletos": Boleto.objects.count(),
        }
        serializer = EstadisticasGeneralesSerializer(data)
        return Response(serializer.data)


class OcupacionVuelosAPIView(APIView):
    """
    GET /api/estadisticas/vuelos_ocupacion/
    Devuelve el porcentaje de ocupación de cada vuelo.
    """
    def get(self, request):
        vuelos = Vuelo.objects.all().select_related("avion", "origen", "destino")
        data = []

        for vuelo in vuelos:
            total_asientos = Asiento.objects.filter(avion=vuelo.avion).count()
            asientos_ocupados = Reserva.objects.filter(
                vuelo=vuelo,
                estado__in=["Confirmada", "Pendiente"],
                activa=True
            ).count()

            porcentaje = (
                (asientos_ocupados / total_asientos) * 100 if total_asientos > 0 else 0
            )

            data.append({
                "vuelo_id": vuelo.id,
                "origen": vuelo.origen.ciudad,
                "destino": vuelo.destino.ciudad,
                "fecha_salida": vuelo.fecha_salida,
                "asientos_totales": total_asientos,
                "asientos_ocupados": asientos_ocupados,
                "porcentaje_ocupacion": round(porcentaje, 2),
            })

        serializer = OcupacionVueloSerializer(data, many=True)
        return Response(serializer.data)


class DestinosPopularesAPIView(APIView):
    """
    GET /api/estadisticas/destinos_populares/
    Devuelve los destinos con más reservas activas.
    """
    def get(self, request):
        destinos = (
            Reserva.objects.filter(activa=True)
            .values("vuelo__destino__ciudad")
            .annotate(total_reservas=Count("id"))
            .order_by("-total_reservas")[:5]
        )

        data = [
            {
                "destino": d["vuelo__destino__ciudad"],
                "total_reservas": d["total_reservas"],
            }
            for d in destinos
        ]

        serializer = DestinoPopularSerializer(data, many=True)
        return Response(serializer.data)