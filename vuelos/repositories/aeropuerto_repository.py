from vuelos.models import Aeropuerto

class AeropuertoRepository:
    @staticmethod
    def get_all() -> list[Aeropuerto]:
        """Obtener todos los aeropuertos."""
        return Aeropuerto.objects.all().order_by("ciudad")

    @staticmethod
    def get_by_id(aeropuerto_id: int) -> Aeropuerto:
        """Obtener un aeropuerto por ID."""
        try:
            return Aeropuerto.objects.get(pk=aeropuerto_id)
        except Aeropuerto.DoesNotExist:
            raise ValueError("El aeropuerto no existe.")

    @staticmethod
    def create(**kwargs) -> Aeropuerto:
        """Crear un nuevo aeropuerto."""
        return Aeropuerto.objects.create(**kwargs)

    @staticmethod
    def update(aeropuerto: Aeropuerto, **kwargs) -> Aeropuerto:
        """Actualizar un aeropuerto existente."""
        for key, value in kwargs.items():
            setattr(aeropuerto, key, value)
        aeropuerto.save()
        return aeropuerto

    @staticmethod
    def delete(aeropuerto: Aeropuerto) -> bool:
        """Eliminar un aeropuerto."""
        try:
            aeropuerto.delete()
            return True
        except Aeropuerto.DoesNotExist:
            return False
