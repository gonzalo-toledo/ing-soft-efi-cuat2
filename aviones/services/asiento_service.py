from aviones.models import Asiento, Avion
from aviones.repositories.asiento_repository import AsientoRepository
from vuelos.repositories.vuelo_repository import VueloRepository
from django.core.exceptions import ValidationError

class AsientoService:
    @staticmethod
    def get_all() -> list[Asiento]:
        """
        Obtener todos los asientos.
        """
        return AsientoRepository.get_all()
    
    @staticmethod
    def get_by_id(asiento_id: int) -> Asiento:
        """
        Obtener un asiento por su ID.
        """
        return AsientoRepository.get_by_id(asiento_id)
    
    @staticmethod
    def create(
        avion: Avion,
        numero: str,
        fila: int,
        columna: str,
        tipo: str
    ) -> Asiento:
        """
        Crear un nuevo asiento.
        """
        return AsientoRepository.create(
            avion=avion,
            numero=numero,
            fila=fila,
            columna=columna,
            tipo=tipo
        )       
        
    @staticmethod
    def delete(asiento_id: int) -> bool:
        """
        Eliminar un asiento.
        """
        try:
            asiento = AsientoRepository.get_by_id(asiento_id)
            return AsientoRepository.delete(asiento)
        except ValueError:
            return False
    
    @staticmethod
    def update(
        asiento_id: int,
        numero: str | None = None,
        fila: int | None = None,
        columna: str | None = None,
        tipo: str | None = None
    ) -> Asiento | ValueError:
        """
        Actualizar un asiento existente.
        """
        try:
            asiento = AsientoRepository.get_by_id(asiento_id)    
            return AsientoRepository.update(
                asiento=asiento,
                numero=numero,
                fila=fila,
                columna=columna,
                tipo=tipo       
            )
        except ValueError as e:
            return e
        
    @staticmethod
    def get_by_avion(avion_id: int) -> list[Asiento]:
        """
        Obtener todos los asientos de un avión específico.
        """
        return AsientoRepository.get_by_avion(avion_id)
    
    @staticmethod
    def verificar_disponibilidad(vuelo_id: int, asiento_id: int) -> dict:
        """
        Verifica si un asiento pertenece al avión del vuelo y si está disponible.
        """
        vuelo = VueloRepository.get_by_id(vuelo_id)
        asiento = AsientoRepository.get_by_id(asiento_id)

        # Validar que el asiento pertenece al avión de este vuelo
        if asiento.avion_id != vuelo.avion_id:
            raise ValidationError("El asiento no pertenece al avión asignado al vuelo.")

        # Verificar si está ocupado
        disponible = AsientoRepository.esta_disponible(asiento_id, vuelo_id)

        return {
            "vuelo_id": vuelo.id,
            "asiento_id": asiento.id,
            "disponible": disponible,
            "mensaje": (
                "El asiento está disponible para este vuelo."
                if disponible
                else "El asiento ya está reservado para este vuelo."
            ),
        }