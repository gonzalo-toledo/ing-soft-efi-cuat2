from reservas.repositories.reserva_repository import ReservaRepository
from reservas.models import Reserva
from pasajeros.models import Pasajero
from vuelos.models import Vuelo
from aviones.models import Asiento
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

class ReservaService:
    
    @staticmethod
    def crear_reserva(user,data):
        """
        crea una nueva reserva solo si el pasajero pertenece al usuario autenticado y no existe una reserva previa para el mismo vuelo.
        """
        pasajero_id = data.get('pasajero')
        vuelo_id = data.get('vuelo')
        asiento_id = data.get('asiento')

        pasajero = get_object_or_404(Pasajero, pk=pasajero_id)
        vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
        asiento = get_object_or_404(Asiento, pk=asiento_id)
        
        # validar pertenencia del pasajero
        if pasajero.usuario.id != user.id:
            raise ValidationError("El pasajero no pertenece al usuario autenticado.")
        
        # Validar duplicados
        if Reserva.objects.filter(pasajero=pasajero, vuelo=vuelo, activa=True).exists():
            raise ValidationError("El pasajero ya tiene una reserva activa para este vuelo.")

        # Verificar disponibilidad del asiento
        if Reserva.objects.filter(asiento=asiento, vuelo=vuelo, activa=True).exists():
            raise ValidationError("El asiento ya está reservado para este vuelo.")

        return ReservaRepository.create(
            pasajero=pasajero,
            vuelo=vuelo,
            asiento=asiento
        )

    @staticmethod
    def cambiar_estado(reserva_id, nuevo_estado):
        """
        Cambia el estado de una reserva (Confirmada o Cancelada).
        """
        reserva = ReservaRepository.get_by_id(reserva_id)

        if nuevo_estado not in ["Confirmada", "Cancelada"]:
            raise ValidationError("El estado debe ser 'Confirmada' o 'Cancelada'.")

        if nuevo_estado == "Cancelada":
            # Liberar asiento y marcar inactiva
            reserva.asiento.ocupado = False
            reserva.asiento.save()
            return ReservaRepository.update(reserva, estado="Cancelada", activa=False)

        elif nuevo_estado == "Confirmada":
            # Generar boleto si no lo tiene
            reserva.generar_boleto()
            return ReservaRepository.update(reserva, estado="Confirmada")

    @staticmethod
    def seleccionar_asiento(reserva_id, asiento_id):
        """
        Cambia el asiento asignado a una reserva, verificando disponibilidad.
        """
        reserva = ReservaRepository.get_by_id(reserva_id)
        nuevo_asiento = get_object_or_404(Asiento, pk=asiento_id)

        # Verificar que el asiento pertenece al mismo avión del vuelo
        if nuevo_asiento.avion != reserva.vuelo.avion:
            raise ValidationError("El asiento seleccionado no pertenece al avión del vuelo.")

        # Verificar que no esté ocupado
        if Reserva.objects.filter(asiento=nuevo_asiento, vuelo=reserva.vuelo, activa=True).exists():
            raise ValidationError("El asiento seleccionado ya está ocupado en este vuelo.")

        # Asignar nuevo asiento
        reserva.asiento = nuevo_asiento
        return ReservaRepository.update(reserva, asiento=nuevo_asiento)

    @staticmethod
    def cancelar_reserva(reserva_id):
        reserva = ReservaRepository.get_by_id(reserva_id)
        reserva.estado = 'Cancelada'
        return ReservaRepository.update(reserva, estado='Cancelada')

    @staticmethod
    def get_all():
        return ReservaRepository.get_all()

    @staticmethod
    def get_by_user(user):
        return ReservaRepository.get_by_user(user)

    @staticmethod
    def get_flight_reservations(vuelo_id):
        return ReservaRepository.get_flight_reservations(vuelo_id)
    
    @staticmethod
    def get_by_asiento(asiento_id):
        return ReservaRepository.get_by_asiento(asiento_id)
    
    @staticmethod
    def get_by_id(reserva_id):
        return ReservaRepository.get_by_id(reserva_id)
    
    @staticmethod
    def get_by_pasajero(pasajero_id):
        return ReservaRepository.get_by_pasajero(pasajero_id)
    
    @staticmethod
    def get_reservas_by_pasajero(pasajero_id):
        return ReservaRepository.get_reservas_by_pasajero(pasajero_id)
    
    @staticmethod
    def delete(reserva):
        return ReservaRepository.delete(reserva)
    
    