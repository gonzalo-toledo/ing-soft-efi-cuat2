from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
    ListAPIView,
)
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)  # Se usa con permission_classes
from django.http import Http404
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
from vuelos.models import Vuelo
from aviones.models import Asiento 

#servicios de pasajeros
from pasajeros.services.pasajero_service import PasajeroService

#servicios de aviones
from aviones.services.avion_service import AvionService
from aviones.services.asiento_service import AsientoService
from api.serializers import AvionSerializer, AsientoSerializer

# Servicios de vuelos
from vuelos.services.aeropuerto_service import AeropuertoService
from vuelos.services.vuelo_service import VueloService

#servicios de reservas
from reservas.services.reserva_service import ReservaService

#servicios de boletos
from reservas.services.boleto_service import BoletoService

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
class PasajeroListCreateView(AuthViewMixin, ListCreateAPIView):
    """
    GET /api/users/<user_pk>/pasajeros/ -> lista pasajeros del usuario
    POST /api/users/<user_pk>/pasajeros/ -> crea pasajero para el usuario
    """

    serializer_class = PasajeroSerializer

    # redefino el queryset para filtrar por usuario:
    def get_queryset(self):
        user_pk = self.kwargs["user_pk"]
        return PasajeroService.obtener_por_usuario(user_pk)

    def perform_create(self, serializer):
        user_pk = self.kwargs["user_pk"]  # obtengo el user_pk de la URL
        usuario = get_object_or_404(User, pk=user_pk)
        data = serializer.validated_data
        data['usuario'] = usuario
        pasajero = PasajeroService.registrar_pasajero(data)
        serializer.instance = pasajero

class PasajeroDetailView(AuthViewMixin, RetrieveAPIView): #RetrieveAPIView hace solo GET
    """
    GET /api/pasajeros/<id>/ -> detalle de un pasajero
    """

    serializer_class = PasajeroSerializer
    # queryset = Pasajero.objects.all()  # requerido por DRF para get_object()

    def get_object(self):
        user_pk = self.kwargs["user_pk"]
        pasajero_pk = self.kwargs["pk"]
        pasajero = PasajeroService.obtener_por_id(pasajero_pk)
        if pasajero.usuario_id != user_pk:
            raise Http404("Este pasajero no pertenece al usuario indicado.")
        return pasajero

class PasajeroReservasView(AuthViewMixin, ListAPIView):
    """
    GET /api/pasajeros/<id>/reservas/ -> lista reservas de un pasajero
    """

    serializer_class = ReservaSerializer

    def get_queryset(self):
        user_pk = self.kwargs["user_pk"]
        pasajero_pk = self.kwargs["pk"]
        pasajero = PasajeroService.obtener_por_id(pasajero_pk)
        if pasajero.usuario_id != user_pk:
            raise Http404("Este pasajero no pertenece al usuario indicado.")
        return PasajeroService.obtener_reservas(pasajero_pk)

# USUARIO + PASAJERO
class RegistroCreateView(CreateAPIView):
    """
    POST /api/registro/ -> crea un nuevo usuario + pasajero
    """

    queryset = Pasajero.objects.all()
    serializer_class = RegistroSerializer


# AEROPUERTOS (con APIView)
class AeropuertoListCreateAPIView(APIView, AuthAdminViewMixin):
    """
    GET /api/aeropuertos/ -> lista todos los aeropuertos
    POST /api/aeropuertos/ -> crea un nuevo aeropuerto
    """

    def get(self, request):
        aeropuertos = AeropuertoService.get_all()
        serializer = AeropuertoSerializer(aeropuertos, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AeropuertoSerializer(data=request.data)
        if serializer.is_valid():
            aeropuerto = AeropuertoService.create(**serializer.validated_data)
            return Response(
                AeropuertoSerializer(aeropuerto).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AeropuertoDetailAPIView(APIView, AuthAdminViewMixin):
    """
    GET /api/aeropuertos/<id>/ -> detalle de un aeropuerto
    PUT /api/aeropuertos/<id>/ -> actualizar aeropuerto
    DELETE /api/aeropuertos/<id>/ -> eliminar aeropuerto
    """

    def get(self, request, pk):
        try:
            aeropuerto = AeropuertoService.get_by_id(pk)
            serializer = AeropuertoSerializer(aeropuerto)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        serializer = AeropuertoSerializer(data=request.data)
        if serializer.is_valid():
            aeropuerto = AeropuertoService.update(pk, **serializer.validated_data)
            return Response(AeropuertoSerializer(aeropuerto).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            ok = AeropuertoService.delete(pk)
            if ok:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"detail": "No se pudo eliminar el aeropuerto"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

# AVIONES

class AvionListCreateAPIView(APIView, AuthAdminViewMixin):
    """
    GET /api/aviones/ -> lista todos los aviones
    POST /api/aviones/ -> crea un nuevo avión
    """

    def get(self, request):
        aviones = AvionService.get_all()
        serializer = AvionSerializer(aviones, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AvionSerializer(data=request.data)
        if serializer.is_valid():
            avion = AvionService.create(**serializer.validated_data)
            return Response(AvionSerializer(avion).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvionDetailAPIView(APIView, AuthAdminViewMixin):
    """
    GET /api/aviones/<id>/ -> detalle de un avión
    PUT /api/aviones/<id>/ -> actualizar avión
    DELETE /api/aviones/<id>/ -> eliminar avión
    """

    def get(self, request, pk):
        try:
            avion = AvionService.get_by_id(pk)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(AvionSerializer(avion).data)

    def put(self, request, pk):
        serializer = AvionSerializer(data=request.data)
        if serializer.is_valid():
            avion = AvionService.update(pk, **serializer.validated_data)
            return Response(AvionSerializer(avion).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ok = AvionService.delete(pk)
        if ok:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'No se pudo eliminar el avión'}, status=status.HTTP_400_BAD_REQUEST)


class AsientoListAPIView(APIView, AuthAdminViewMixin):
    """
    GET /api/asientos/ -> lista todos los asientos
    GET /api/aviones/<avion_id>/asientos/ -> lista asientos de un avión
    """

    def get(self, request, avion_id=None):
        if avion_id:
            asientos = AsientoService.get_by_avion(avion_id)
        else:
            asientos = AsientoService.get_all()
        serializer = AsientoSerializer(asientos, many=True)
        return Response(serializer.data)



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



#---------CON APIVIEW Y SERVICIOS ---------

# class VueloListCreateAPIView(APIView, AuthAdminViewMixin):
#     """
#     GET /api/vuelos/ -> lista todos los vuelos (con filtros)
#     POST /api/vuelos/ -> crea un nuevo vuelo
#     """

#     def get(self, request):
#         origen = request.query_params.get("origen")
#         destino = request.query_params.get("destino")
#         fecha = request.query_params.get("fecha")

#         vuelos = VueloService.filter(origen=origen, destino=destino, fecha=fecha)
#         serializer = VueloModelSerializer(vuelos, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = VueloModelSerializer(data=request.data)
#         if serializer.is_valid():
#             vuelo = VueloService.create(**serializer.validated_data)
#             return Response(VueloModelSerializer(vuelo).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class VueloDetailAPIView(APIView, AuthAdminViewMixin):
#     """
#     GET /api/vuelos/<id>/ -> detalle de un vuelo
#     PUT /api/vuelos/<id>/ -> actualizar vuelo
#     DELETE /api/vuelos/<id>/ -> eliminar vuelo
#     """

#     def get(self, request, pk):
#         try:
#             vuelo = VueloService.get_by_id(pk)
#             serializer = VueloModelSerializer(vuelo)
#             return Response(serializer.data)
#         except ValueError as e:
#             return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

#     def put(self, request, pk):
#         serializer = VueloModelSerializer(data=request.data)
#         if serializer.is_valid():
#             vuelo = VueloService.update(pk, **serializer.validated_data)
#             return Response(VueloModelSerializer(vuelo).data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         try:
#             ok = VueloService.delete(pk)
#             if ok:
#                 return Response(status=status.HTTP_204_NO_CONTENT)
#             return Response(
#                 {"detail": "No se pudo eliminar el vuelo"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         except ValueError as e:
#             return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


# --------- CON GENERIC VIEWS Y SERVICIOS ---------
class VueloListCreateAPIView(AuthAdminViewMixin, ListCreateAPIView):
    """
    GET /api/vuelos/ -> lista todos los vuelos (con filtros)
    POST /api/vuelos/ -> crea un nuevo vuelo
    """
    serializer_class = VueloModelSerializer
    queryset = Vuelo.objects.all()

    def get_queryset(self):
        origen = self.request.query_params.get("origen")
        destino = self.request.query_params.get("destino")
        fecha = self.request.query_params.get("fecha")
        return VueloService.filter(origen=origen, destino=destino, fecha=fecha)

    def perform_create(self, serializer):
        """
        Crea un vuelo usando el service y asigna el resultado al serializer.
        """
        validated_data = serializer.validated_data
        vuelo = VueloService.create(**validated_data)
        serializer.instance = vuelo


class VueloDetailAPIView(AuthAdminViewMixin, RetrieveUpdateDestroyAPIView):
    """
    GET /api/vuelos/<id>/ -> detalle de un vuelo
    PUT /api/vuelos/<id>/ -> actualizar vuelo
    DELETE /api/vuelos/<id>/ -> eliminar vuelo
    """
    serializer_class = VueloModelSerializer
    queryset = Vuelo.objects.all()  # requerido por DRF para get_object()

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            return VueloService.get_by_id(pk)
        except ValueError as e:
            raise Http404(str(e))

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        pk = self.kwargs.get("pk")
        vuelo = VueloService.update(pk, **validated_data)
        serializer.instance = vuelo

    def perform_destroy(self, instance):
        pk = self.kwargs.get("pk")
        VueloService.delete(pk)

# =====================================================
# RESERVAS
# =====================================================
class ReservaAdminListAPIView(AuthAdminViewMixin, ListCreateAPIView):
    """
    GET /api/admin/reservas/ -> lista todas las reservas (solo admin)
    POST /api/admin/reservas/ -> crear una reserva sin restricciones de usuario
    """
    serializer_class = ReservaSerializer

    def get_queryset(self):
        return ReservaService.get_all().order_by("-fecha_reserva")

    def perform_create(self, serializer):
        serializer.save(activa=True, estado="Pendiente")
    
class ReservaListCreateAPIView(AuthViewMixin, ListCreateAPIView):
    serializer_class = ReservaSerializer
    """
    GET /api/reservas/ -> lista reservas del usuario autenticado
    POST /api/reservas/ -> crea una nueva reserva para el usuario autenticado    
    """
    def get_queryset(self):
        # Solo reservas del usuario autenticado
        return ReservaService.get_by_user(self.request.user).order_by("-fecha_reserva")
    
    def get_serializer_context(self):
        # Pasar el request al serializer (para filtrar pasajeros)
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    
class ReservaDetailAPIView(AuthViewMixin, APIView):
    """
    GET /api/reservas/<id>/estado/ -> detalle del estado de una reserva
    PATCH /api/reservas/<id>/estado/ -> cambiar el estado de una reserva (Confirmada / Cancelada)
    """
    def get(self, request, pk):
        reserva = ReservaService.get_by_id(pk)
        return Response(
            {"id": reserva.id, "estado": reserva.estado},
            status=status.HTTP_200_OK
        )
    
    def patch(self, request, pk):
        # Garantizá que sea del usuario logueado
        get_object_or_404(
            ReservaService.get_by_user(request.user), pk=pk
        )
        
        nuevo_estado = request.data.get("estado")
        if nuevo_estado not in ["Confirmada", "Cancelada"]:
            return Response(
                {"detail": "El estado debe ser Confirmada o Cancelada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reserva = ReservaService.cambiar_estado(pk, nuevo_estado)
            return Response(ReservaSerializer(reserva).data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class ReservaDetailAPIView(APIView, AuthViewMixin):
#     """
#     GET /api/reservas/<id>/ -> detalle de una reserva
#     UPDATE /api/reservas/<id>/ -> actualizar reserva
#     DELETE /api/reservas/<id>/ -> eliminar reserva
#     """

#     def get(self, request, pk):
#         reserva = get_object_or_404(
#             Reserva.objects.select_related("vuelo", "pasajero", "asiento"), pk=pk
#         )
#         serializer = ReservaSerializer(reserva)
#         return Response(serializer.data)
    
#     def put(self, request, pk):
#         reserva = get_object_or_404(
#             Reserva.objects.select_related("vuelo", "pasajero", "asiento"), pk=pk
#         )
#         serializer = ReservaSerializer(reserva, data=request.data)
#         if serializer.is_valid():
#             reserva = serializer.save()
#             return Response(ReservaSerializer(reserva).data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self, request, pk):
#         reserva = get_object_or_404(
#             Reserva.objects.select_related("vuelo", "pasajero", "asiento"), pk=pk
#         )
#         reserva.delete()
#         return Response(
#             {"detail": "Reserva eliminada correctamente."},
#             status=status.HTTP_204_NO_CONTENT,
#         )

# class CrearReservaAPIView(AuthViewMixin, APIView):
#     """
#     POST /api/pasajeros/<pasajero_id>/vuelos/<vuelo_id>/reservas/
#     Crea una reserva para un pasajero en un vuelo.
#     """

#     def post(self, request, pasajero_id, vuelo_id):
#         asiento_id = request.data.get("asiento_id")

#         data = {
#             "pasajero": pasajero_id,
#             "vuelo": vuelo_id,
#             "asiento": asiento_id,
#         }

#         try:
#             reserva = ReservaService.crear_reserva(request.user, data)
#             serializer = ReservaSerializer(reserva)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"detail": f"Error al crear la reserva: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        
# =====================================================
# BOLETOS
# =====================================================
    
class BoletoAdminListApiView(AuthAdminViewMixin, ListAPIView):
    """
    GET /api/admin/boletos/ -> listar todos los boletos (solo admin)
    """
    
    serializer_class = BoletoSerializer
    
    def get_queryset(self):
        return BoletoService.get_all().order_by("-fecha_emision")

class BoletoListApiView(AuthViewMixin, ListAPIView):
    """
    GET /api/boletos/ -> listar boletos del usuario autenticado
    """

    serializer_class = BoletoSerializer

    def get_queryset(self):
        return BoletoService.get_by_user(self.request.user).order_by("-fecha_emision")


class BoletoPorCodiogoAPIView(AuthViewMixin, RetrieveAPIView):
    """
    GET /api/boletos/codigo/<codigo_barra>/ -> detalle de un boleto por código de barra
    """
    
    serializer_class = BoletoSerializer
    
    def get_object(self):
        codigo_barra = self.kwargs["codigo_barra"]
        return BoletoService.get_by_codigo_barra(codigo_barra, self.request.user)

# class BoletoListCreateAPIView(ListCreateAPIView, AuthViewMixin):
#     """
#     GET /api/boletos/ -> listar boletos
#     POST /api/boletos/ -> generar nuevo boleto desde reserva confirmada
#     """

#     queryset = (
#         Boleto.objects.select_related("reserva", "reserva__vuelo")
#         .all()
#         .order_by("-fecha_emision")
#     )
#     serializer_class = BoletoSerializer


# class BoletoDetailAPIView(RetrieveUpdateDestroyAPIView, AuthViewMixin):
#     """
#     GET /api/boletos/<id>/ -> detalle de un boleto
#     PUT /api/boletos/<id>/ -> actualizar boleto
#     DELETE /api/boletos/<id>/ -> eliminar boleto
#     """

#     queryset = (
#         Boleto.objects.select_related("reserva", "reserva__vuelo")
#         .all()
#         .order_by("-fecha_emision")
#     )
#     serializer_class = BoletoSerializer


#====================================================
# ESTADISTICAS GENERALES DE VUELOS
#====================================================

class EstadisticasGeneralesAPIView(APIView, AuthAdminViewMixin):
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


class OcupacionVuelosAPIView(APIView, AuthAdminViewMixin):
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


class DestinosPopularesAPIView(APIView, AuthViewMixin):
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