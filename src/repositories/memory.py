"""
In-memory repository implementation

This implementation stores devices in a dictionary. It's useful for:
1. Unit testing (fast, no external dependencies)
2. Development and prototyping
3. Understanding the repository pattern before adding persistence

Data is lost when the process exits.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from src.models.device import Device, DeviceCreate, DeviceUpdate
from src.repositories.base import DeviceRepository
from src.repositories.exceptions import DuplicateDeviceError


class InMemoryDeviceRepository(DeviceRepository):
    """
    Dictionary-based device repository.

    Devices are stored in a dict keyed by UUID. We also maintain
    secondary indexes for hostname and IP lookups.

    Thread Safety: This implementation is NOT thread-safe.
    For concurrent access, you'd need locks or a thread-sade dict.
    """

    def __init__(self):
        """Initialize empty storage."""
        self._devices: dict[UUID, Device] = {}
        # Secondary indexes for dast lookups
        self._hostname_index: dict[str, UUID] = {}
        self._ip_index: dict[str, UUID] ={}

    def add(self, device_data: DeviceCreate) -> Device:
        """
        Add a new device to memory


        We check for duplicates using our secondary indexes before
        creating the device. This ensures uniqueness of hostname and IP.
        """

        # Check for duplicate hostname
        if device_data.hostname in self._hostname_index:
            raise DuplicateDeviceError("hostname", device_data.hostname)

        # Check for duplicate IP
        ip_str = str(device_data.management_ip)
        if ip_str in self._ip_index:
            raise DuplicateDeviceError("management_ip", ip_str)

        # Create the full Device from the create schema
        device = Device (
            hostname=device_data.hostname,
            management_ip=device_data.management_ip,
            platform=device_data.platform,
            role=device_data.role,
            site=device_data.site,
        )

        # Store in primary and secondary indexes
        self._devices[device.id] = device
        self._hostname_index[device.hostname] = device.id
        self._ip_index[str(device.management_ip)] = device.id

        return device

    def get_by_id(self, device_id: UUID) -> Optional[Device]:
        """Direct dictionary lookup by UUID."""
        return self._devices.get(device_id)

    def get_by_hostname(self, hostname: str) -> Optional[Device]:
        """
        Two-step lookup: hostname -> UUID -> Device.

        This is O(1) thanks to the secondary index.
        """
        device_id = self._hostname_index.get(hostname)
        if device_id is None:
            return None
        return self._devices.get(device_id)

    def get_all(self) -> list[Device]:
        """Return all devices as a list."""
        return list(self._devices.values())

    def update(self, device_id: UUID, update_data: DeviceUpdate) -> Optional[Device]:
        """
        Update a device with partial data.

        Because Device is immutable (frozen), we create a new instance
        with the updated fields. This is the safe pattern for immutable data.
        """
        existing = self._devices.get(device_id)
        if existing is None:
            return None

        # Get non-None fields from update_data
        # model_dump(exclude_unset=True) returns only explicitly set fields
        updates = update_data.model_dump(exclude_unset=True)

        if not updates:
            return existing  # Nothing to update

        # Check for duplicate hostname if it's being changed
        if "hostname" in updates and updates["hostname"] != existing.hostname:
            if updates["hostname"] in self._hostname_index:
                raise DuplicateDeviceError("hostname", updates["hostname"])

        # Check for duplicate IP if it's being changed
        if "management_ip" in updates:
            new_ip = str(updates["management_ip"])
            if new_ip != str(existing.management_ip) and new_ip in self._ip_index:
                raise DuplicateDeviceError("management_ip", new_ip)

        # Add updated_at timestamp
        updates["updated_at"] = datetime.now()

        # Create new device with updates
        # model_copy creates a copy with specified field changes
        updated_device = existing.model_copy(update=updates)

        # Update indexes if hostname or IP changed
        if updated_device.hostname != existing.hostname:
            del self._hostname_index[existing.hostname]
            self._hostname_index[updated_device.hostname] = device_id

        if str(updated_device.management_ip) != str(existing.management_ip):
            del self._ip_index[str(existing.management_ip)]
            self._ip_index[str(updated_device.management_ip)] = device_id

        # Store updated device
        self._devices[device_id] = updated_device

        return updated_device

    def delete(self, device_id: UUID) -> bool:
        """
        Remove a device and clean up all indexes.

        Returns True if deleted, False if device didn't exist.
        """
        device = self._devices.get(device_id)
        if device is None:
            return False

        # Remove from all indexes
        del self._devices[device_id]
        del self._hostname_index[device.hostname]
        del self._ip_index[str(device.management_ip)]

        return True

    def filter_by(
            self,
            platform: Optional[str] = None,
            role: Optional[str] = None,
            site: Optional[str] = None,
    ) -> list[Device]:
        """
        Filter devices by criteria using list comprehension.

        All provided criteria must match (AND logic).
        None values are ignored (wildcard).
        """
        results = []

        for device in self._devices.values():
            # Check each criterion if provided
            if platform is not None and device.platform.value != platform:
                continue
            if role is not None and device.role.value != role:
                continue
            if site is not None and device.site != site:
                continue

            results.append(device)

        return results

