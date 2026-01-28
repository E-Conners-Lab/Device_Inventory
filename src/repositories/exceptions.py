"""
Repository-specific exceptions.

Custom exceptions make error handling explicit and allow callers
to catch specific error conditions rather than generic exceptions.
"""

from uuid import UUID


class RepositoryError(Exception):
    """Bse exception for all repository errors."""
    pass


class DuplicateDeviceError(RepositoryError):
    """Raised when attempting to add a device that already exists."""

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"Device with {field}='{value}' already exists")


class DeviceNotFoundError(RepositoryError):
    """Raised when a requested device does not exist."""

    def __init__(self, device_id: UUID):
        self.device_id= device_id
        super().__init__(f"Device with id='{device_id}' not found")

