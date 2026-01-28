"""
Repository interface definitions.

This module defines the abstract base class that all repository
implementations must follow. This is the "contract" that the rest
of the application depends on.

Why an abstract base class?
1. Documents the expected interface clearly
2. Enforces implementation of all required methods
3. Allows type hints to reference the base class
4. Makes it easy to swap implementations (memory, JSON, database)
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.models.device import Device, DeviceCreate, DeviceUpdate

class DeviceRepository(ABC):
    """
    Abstract base class for device storage operations.

    All repository implementations must provide these methods.
    The service layer depends only on this interface, not on
    concrete implementations.

    This follows the Dependency Inversion Principle:
    "Depend on abstractions, not concretions."
    """

    @abstractmethod
    def add(self, device_data: DeviceCreate) -> Device:
        """
        Add a new device to the repository.

        Args:
            device_data: Validated device creation data

        Returns:
            The created Device with generated id and timestamps

        Raises:
             DuplicateDeviceError: If hostname or IP already exists
        """
        pass

    @abstractmethod
    def get_by_id(self, device_id: UUID) -> Optional[Device]:
        """
        Retrieve a device by its unique identifier

        Args:
            device_id: The UUID of the device

        Returns:
              The Device if found, None otherwise
        """
        pass

    @abstractmethod
    def get_by_hostname(self, hostname: str) -> Optional[Device]:
        """
        Retrieve a device by its hostname

        Args:
             hostname: The device hostname

        Returns:
              The Device if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Device]:
        """
        Retrieve all devices in the repository

        Returns:
            List of all devices, empty list if none exist.
        """
        pass

    @abstractmethod
    def update(self, device_id: UUID, update_data: DeviceUpdate) -> Optional[Device]:
        """
        Update an existing device

        Args:
            device_id: The UUID of the device to update
            update_data:: Fields to update (None values are ignored)

        Returns:
              The updated Device if found, None if device doesn't exist
        """
        pass

    @abstractmethod
    def delete(self, device_id: UUID) -> bool:
        """
        Remove a device from the repository.

        Args:
            device_id: The UUID of the device to delete

        Returns:
              True if device was deleted, False if not found
        """
        pass

    @abstractmethod
    def filter_by(
    self,
    platform: Optional[str] = None,
    role: Optional[str] = None,
    site: Optional[str] = None,
    ) -> list[Device]:
        """
        Filter device by specified criteria

        Args:
            platform: Filter by platform (e.g., "ios_xe")
            role: Filter by role (e.g., "spine")
            site: Filter by site (e.g., "dc1")

        Returns:
              List of devices matching all provided criteria
        """
        pass