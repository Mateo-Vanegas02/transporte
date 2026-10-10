class DomainException(Exception):
    """Excepción base para el dominio de la aplicación."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EntityNotFoundException(DomainException):
    """Excepción lanzada cuando una entidad solicitada no existe."""

    pass


class ConductorNotFoundException(EntityNotFoundException):
    def __init__(self, id_conductor: int) -> None:
        super().__init__(f"Conductor con ID {id_conductor} no fue encontrado.")
        self.id_conductor = id_conductor


class VehiculoNotFoundException(EntityNotFoundException):
    def __init__(self, id_vehiculo: int) -> None:
        super().__init__(f"Vehículo con ID {id_vehiculo} no fue encontrado.")
        self.id_vehiculo = id_vehiculo


class ViajeNotFoundException(EntityNotFoundException):
    def __init__(self, id_viaje: int) -> None:
        super().__init__(f"Viaje con ID {id_viaje} no fue encontrado.")
        self.id_viaje = id_viaje


class DuplicateEntityException(DomainException):
    """Excepción lanzada cuando ocurre una colisión de campo único."""

    pass


class LicenciaAlreadyExistsException(DuplicateEntityException):
    def __init__(self, licencia: str) -> None:
        super().__init__(f"La licencia '{licencia}' ya se encuentra registrada.")
        self.licencia = licencia


class PlacaAlreadyExistsException(DuplicateEntityException):
    def __init__(self, placa: str) -> None:
        super().__init__(f"La placa '{placa}' ya se encuentra registrada.")
        self.placa = placa


class EntityInUseException(DomainException):
    """
    Excepción lanzada cuando una entidad no puede eliminarse por tener
    dependencias activas.
    """

    pass


class ConductorHasVehiculosException(EntityInUseException):
    def __init__(self, id_conductor: int) -> None:
        super().__init__(
            f"No se puede eliminar el conductor con ID {id_conductor} "
            "porque tiene vehículos asociados."
        )
        self.id_conductor = id_conductor


class VehiculoHasViajesException(EntityInUseException):
    def __init__(self, id_vehiculo: int) -> None:
        super().__init__(
            f"No se puede eliminar el vehículo con ID {id_vehiculo} "
            "porque tiene viajes asociados."
        )
        self.id_vehiculo = id_vehiculo
