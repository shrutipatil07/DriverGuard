"""
Domain exceptions for DriverGuard.
"""


class DomainException(Exception):
    """Base exception for all domain-level errors."""
    pass


class DriverNotFoundError(DomainException):
    """Raised when a requested driver cannot be found."""

    def __init__(self, driver_id: int):
        self.driver_id = driver_id
        super().__init__(f"Driver with id {driver_id} does not exist.")


class UserNotFoundError(DomainException):
    """Raised when a requested user cannot be found."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} does not exist.")


class DeviceNotFoundError(DomainException):
    """Raised when a requested device cannot be found."""

    def __init__(self, device_id: int):
        self.device_id = device_id
        super().__init__(f"Device with id {device_id} does not exist.")


class DuplicateDriverError(DomainException):
    """Raised when driver unique constraint is violated."""

    def __init__(self, field_name: str, field_value: str):
        self.field_name = field_name
        self.field_value = field_value
        super().__init__(f"A driver with {field_name} '{field_value}' already exists.")


class DuplicateUserError(DomainException):
    """Raised when user unique email is violated."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"A user with email '{email}' already exists.")


class DuplicateDeviceError(DomainException):
    """Raised when device serial number is violated."""

    def __init__(self, serial_number: str):
        self.serial_number = serial_number
        super().__init__(f"A device with serial number '{serial_number}' already exists.")
