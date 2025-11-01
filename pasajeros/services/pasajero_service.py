from pasajeros.repositories.pasajero_repository import PasajeroRepository
from reservas.repositories.reserva_repository import ReservaRepository
from django.http import Http404

class PasajeroService:

    @staticmethod
    def registrar_pasajero(data):
        """ Registra un nuevo pasajero en el sistema.

        :param data: Diccionario con los datos del pasajero.
        :return: Instancia del pasajero creado.
        """
        # Validaciones
        if 'pasaporte' not in data:
            raise ValueError("El pasaporte es obligatorio para registrar un pasajero.")
        
        # Verificar si ya existe un pasajero con el mismo pasaporte
        existing_pasajero = PasajeroRepository.get_by_pasaporte(data['pasaporte'])
        if existing_pasajero:
            raise ValueError("Ya existe un pasajero con este pasaporte.")

        # Crear el pasajero
        return PasajeroRepository.create(**data)

    @staticmethod
    def obtener_todos():
        """ Obtiene todos los pasajeros registrados en el sistema.
        :return: Lista de instancias de Pasajero.
        """
        return PasajeroRepository.get_all()

    @staticmethod
    def obtener_por_id(pasajero_id):
        """ Obtiene un pasajero por su ID.
        :param pasajero_id: ID del pasajero a buscar.
        :return: Instancia del pasajero.
        """
        return PasajeroRepository.get_by_id(pasajero_id)
    
    @staticmethod
    def obtener_por_usuario(user_id):
        """ Obtiene todos los pasajeros asociados a un usuario.
        :param user_id: ID del usuario.
        :return: Lista de instancias de Pasajero.
        """
        return PasajeroRepository.get_all_by_user(user_id)
    
    @staticmethod
    def obtener_reservas(pasajero_id, estado=None):
        """
        Devuelve las reservas de un pasajero (filtradas opcionalmente por estado).
        """
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        if not pasajero:
            raise Http404("Pasajero no encontrado.")

        return ReservaRepository.filter_by_pasajero(pasajero.id, estado)

    @staticmethod
    def eliminar_pasajero(pasajero_id):
        """ Elimina un pasajero del sistema por su ID.
        :param pasajero_id: ID del pasajero a eliminar.
        :return: None
        """
        # Verificar si el pasajero existe
        if not PasajeroRepository.get_by_id(pasajero_id):
            raise ValueError("Pasajero no encontrado.")
        
        # Eliminar el pasajeroS
        pasajero = PasajeroRepository.get_by_id(pasajero_id)
        PasajeroRepository.delete(pasajero)
