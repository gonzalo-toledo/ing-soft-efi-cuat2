from reservas.models import Pasajero, Reserva
from django.shortcuts import get_object_or_404

class PasajeroRepository:

    @staticmethod
    def get_all():
        return Pasajero.objects.all()
    
    @staticmethod
    def get_all_by_user(user_id):
        return Pasajero.objects.filter(usuario=user_id)

    @staticmethod
    def get_by_id(pasajero_id):
        return get_object_or_404(Pasajero, id=pasajero_id)

    @staticmethod
    def get_by_pasaporte(pasaporte):
        return Pasajero.objects.filter(pasaporte=pasaporte).first()
    
    @staticmethod
    def get_reservas_by_pasajero(pasajero_id: int):
        return Reserva.objects.filter(pasajero_id=pasajero_id).select_related("vuelo", "asiento")

    @staticmethod
    def create(**kwargs):
        return Pasajero.objects.create(**kwargs)

    @staticmethod
    def update(pasajero, **kwargs):
        for attr, value in kwargs.items():
            setattr(pasajero, attr, value)
        pasajero.save()
        return pasajero

    @staticmethod
    def delete(pasajero):
        pasajero.delete()
