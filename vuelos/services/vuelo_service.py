from vuelos.repositories.vuelo_repository import VueloRepository
from vuelos.models import Vuelo

class VueloService:
    @staticmethod
    def get_all() -> list[Vuelo]:
        return VueloRepository.get_all()

    @staticmethod
    def get_by_id(vuelo_id: int) -> Vuelo:
        return VueloRepository.get_by_id(vuelo_id)

    @staticmethod
    def filter(origen=None, destino=None, fecha=None) -> list[Vuelo]:
        return VueloRepository.filter(origen, destino, fecha)

    @staticmethod
    def create(**kwargs) -> Vuelo:
        return VueloRepository.create(**kwargs)

    @staticmethod
    def update(vuelo_id: int, **kwargs) -> Vuelo:
        vuelo = VueloRepository.get_by_id(vuelo_id)
        return VueloRepository.update(vuelo, **kwargs)

    @staticmethod
    def delete(vuelo_id: int) -> bool:
        vuelo = VueloRepository.get_by_id(vuelo_id)
        return VueloRepository.delete(vuelo)

    @staticmethod
    def actualizar_estado(vuelo_id: int) -> Vuelo:
        """Actualizar el estado de un vuelo individual."""
        vuelo = VueloRepository.get_by_id(vuelo_id)
        vuelo.actualizar_estado()
        return vuelo
