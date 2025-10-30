from vuelos.repositories.aeropuerto_repository import AeropuertoRepository
from vuelos.models import Aeropuerto

class AeropuertoService:
    @staticmethod
    def get_all() -> list[Aeropuerto]:
        return AeropuertoRepository.get_all()

    @staticmethod
    def get_by_id(aeropuerto_id: int) -> Aeropuerto:
        return AeropuertoRepository.get_by_id(aeropuerto_id)

    @staticmethod
    def create(**kwargs) -> Aeropuerto:
        return AeropuertoRepository.create(**kwargs)

    @staticmethod
    def update(aeropuerto_id: int, **kwargs) -> Aeropuerto:
        aeropuerto = AeropuertoRepository.get_by_id(aeropuerto_id)
        return AeropuertoRepository.update(aeropuerto, **kwargs)

    @staticmethod
    def delete(aeropuerto_id: int) -> bool:
        aeropuerto = AeropuertoRepository.get_by_id(aeropuerto_id)
        return AeropuertoRepository.delete(aeropuerto)
