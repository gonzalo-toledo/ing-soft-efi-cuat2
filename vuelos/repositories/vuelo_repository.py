from vuelos.models import Vuelo

class VueloRepository:
    @staticmethod
    def get_all() -> list[Vuelo]:
        """Obtener todos los vuelos."""
        return Vuelo.objects.select_related("avion", "origen", "destino").all()

    @staticmethod
    def get_by_id(vuelo_id: int) -> Vuelo:
        """Obtener un vuelo por su ID."""
        try:
            return Vuelo.objects.select_related("avion", "origen", "destino").get(pk=vuelo_id)
        except Vuelo.DoesNotExist:
            raise ValueError("El vuelo no existe.")

    @staticmethod
    def filter(origen=None, destino=None, fecha=None) -> list[Vuelo]:
        """Filtrar vuelos por origen, destino o fecha."""
        qs = Vuelo.objects.select_related("avion", "origen", "destino").all()
        if origen:
            qs = qs.filter(origen__iata__iexact=origen)
        if destino:
            qs = qs.filter(destino__iata__iexact=destino)
        if fecha:
            qs = qs.filter(fecha_salida__date=fecha)
        return qs

    @staticmethod
    def create(**kwargs) -> Vuelo:
        """Crear un vuelo."""
        return Vuelo.objects.create(**kwargs)

    @staticmethod
    def update(vuelo: Vuelo, **kwargs) -> Vuelo:
        """Actualizar un vuelo existente."""
        for key, value in kwargs.items():
            setattr(vuelo, key, value)
        vuelo.save()
        return vuelo

    @staticmethod
    def delete(vuelo: Vuelo) -> bool:
        """Eliminar un vuelo."""
        try:
            vuelo.delete()
            return True
        except Vuelo.DoesNotExist:
            return False
