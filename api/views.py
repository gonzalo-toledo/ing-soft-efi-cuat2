from django.contrib.auth.models import User
from pasajeros.models import Pasajero
from vuelos.models import Vuelo, Aeropuerto

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser #Se usa con permission_classes

from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.mixins import AuthViewMixin, AuthAdminViewMixin #permite que le pasemos el permiso como una vista y no como un permission_class (herencia de clase)
from api.permissions import TokenPermission
from api.serializers import (
    UserSerializer, 
    PasajeroSerializer, 
    RegistroSerializer, 
    AeropuertoSerializer, 
    VueloSerializer,
)


# USERS

# class UserListView(ListAPIView):
#     '''
#     GET /api/users/
#       return -> [<UserSerializer>, ...]
#     '''
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
    


class UserListCreateView(ListCreateAPIView):
    '''
    GET /api/users/
        return -> [<UserSerializer>, ...]
    POST /api/users/ - crea un nuevo usuario
    '''
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    '''
    GET /api/users/
        return -> [<UserSerializer>, ...]
    PUT /api/users/1/ -> actualiza el usuario 1
    PATCH /api/users/1/ -> actualiza parcialmente el usuario 1
    DELETE /api/users/1/ -> elimina el usuario 1   
    '''
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
            {"detail": "Usuario desactivado correctamente."},
            status=status.HTTP_200_OK
        )
        


#PASAJEROS
class PasajeroListCreateView(ListCreateAPIView, AuthViewMixin):
    """
    GET /api/users/<user_pk>/pasajeros/ -> lista pasajeros del usuario
    POST /api/users/<user_pk>/pasajeros/ -> crea pasajero para el usuario
    """

    serializer_class = PasajeroSerializer

    # redefino el queryset para filtrar por usuario:
    def get_queryset(self):
        user_pk = self.kwargs['user_pk']
        return Pasajero.objects.filter(usuario_id=user_pk)

    def perform_create(self, serializer):
        user_pk = self.kwargs['user_pk'] # obtengo el user_pk de la URL
        usuario = get_object_or_404(User, pk=user_pk)
        serializer.save(usuario=usuario)



#USUARIO + PASAJERO
class RegistroCreateView(CreateAPIView):
    """
    POST /api/registro/ -> crea un nuevo usuario + pasajero
    """
    queryset = Pasajero.objects.all()
    serializer_class = RegistroSerializer



# AEROPUERTOS (con APIView)
class AeropuertoListCreateAPIView(APIView, AuthAdminViewMixin): #con APIViewtengo que definir get y post
    """
    GET /api/aeropuertos/ -> lista todos los aeropuertos
    POST /api/aeropuertos/ -> crea un nuevo aeropuerto
    """
    def get(self, request):
        qs = Aeropuerto.objects.all().order_by('id')
        serializer = AeropuertoSerializer(qs, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AeropuertoSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                AeropuertoSerializer(instance).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AeropuertoDetailAPIView(APIView, AuthAdminViewMixin):
    """
    GET /api/vuelos/<id>/ -> detalle de un vuelo
    """
    def get_object(self, pk):
        return get_object_or_404(Aeropuerto, pk=pk)
    
    def get(self, request, pk):
        instance = self.get_object(pk)
        return Response(
            AeropuertoSerializer(instance).data
        )
        
    def put(self, request, pk):
        instance = self.get_object(pk)
        serializer = AeropuertoSerializer(instance, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                AeropuertoSerializer(instance).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk):
        instance = self.get_object(pk)
        serializer = AeropuertoSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(
                AeropuertoSerializer(instance).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        instance = self.get_object(pk)
        instance.delete()
        return Response(
            {"detail": "Aeropuerto eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
        

# VUELOS (con APIView)
class VueloListCreateAPIView(APIView):
    """
    GET /api/vuelos/ -> lista todos los vuelos
    POST /api/vuelos/ -> crea un nuevo vuelo
    """
    permission_classes = [TokenPermission]
    def get(self, request):
        qs = Vuelo.objects.all().order_by('id')
        serializer = VueloSerializer(qs, many=True)
        return Response(serializer.data)