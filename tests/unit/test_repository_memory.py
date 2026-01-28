"""
Unit tests for the in-memory device repository.

These tests verify all CRUD operations and edge cases.
We use pytest fixtures to set up clean repository instances.
"""

import pytest
from uuid import uuid4

from src.models.device import DeviceCreate, DevicePlatform, DeviceRole, DeviceUpdate
from src.repositories.memory import InMemoryDeviceRepository
from src.repositories.exceptions import DuplicateDeviceError


@pytest.fixture
def repo():
    """
    Provide a fresh repository for each test.

    Fixtures are pytest's way of handling setup/teardown.
    Each test gets its own instance, ensuring test isolation.
    """
    return InMemoryDeviceRepository()


@pytest.fixture
def sample_device_data():
    """Reusable device creation data."""
    return DeviceCreate(
        hostname="spine1",
        management_ip="10.0.0.1",
        platform=DevicePlatform.EOS,
        role=DeviceRole.SPINE,
        site="dc1",
    )


class TestAdd:
    """Tests for the add operation."""

    def test_add_returns_device_with_id(self, repo, sample_device_data):
        """Adding a device should return it with a generated ID."""
        device = repo.add(sample_device_data)

        assert device.id is not None
        assert device.hostname == "spine1"
        assert str(device.management_ip) == "10.0.0.1"

    def test_add_generates_timestamps(self, repo, sample_device_data):
        """Added devices should have created_at and updated_at set."""
        device = repo.add(sample_device_data)

        assert device.created_at is not None
        assert device.updated_at is not None

    def test_add_duplicate_hostname_raises(self, repo, sample_device_data):
        """Adding a device with duplicate hostname should raise."""
        repo.add(sample_device_data)

        duplicate = DeviceCreate(
            hostname="spine1",  # Same hostname
            management_ip="10.0.0.99",  # Different IP
            platform=DevicePlatform.EOS,
            role=DeviceRole.SPINE,
            site="dc1",
        )

        with pytest.raises(DuplicateDeviceError) as exc_info:
            repo.add(duplicate)

        assert exc_info.value.field == "hostname"
        assert exc_info.value.value == "spine1"

    def test_add_duplicate_ip_raises(self, repo, sample_device_data):
        """Adding a device with duplicate IP should raise."""
        repo.add(sample_device_data)

        duplicate = DeviceCreate(
            hostname="spine2",  # Different hostname
            management_ip="10.0.0.1",  # Same IP
            platform=DevicePlatform.EOS,
            role=DeviceRole.SPINE,
            site="dc1",
        )

        with pytest.raises(DuplicateDeviceError) as exc_info:
            repo.add(duplicate)

        assert exc_info.value.field == "management_ip"


class TestGetById:
    """Tests for get_by_id operation."""

    def test_get_existing_device(self, repo, sample_device_data):
        """Should return the device when it exists."""
        created = repo.add(sample_device_data)

        retrieved = repo.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.hostname == created.hostname

    def test_get_nonexistent_returns_none(self, repo):
        """Should return None for unknown ID."""
        result = repo.get_by_id(uuid4())

        assert result is None


class TestGetByHostname:
    """Tests for get_by_hostname operation."""

    def test_get_existing_by_hostname(self, repo, sample_device_data):
        """Should return device when hostname exists."""
        created = repo.add(sample_device_data)

        retrieved = repo.get_by_hostname("spine1")

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_hostname_returns_none(self, repo):
        """Should return None for unknown hostname."""
        result = repo.get_by_hostname("nonexistent")

        assert result is None


class TestGetAll:
    """Tests for get_all operation."""

    def test_empty_repo_returns_empty_list(self, repo):
        """Empty repository should return empty list."""
        result = repo.get_all()

        assert result == []

    def test_returns_all_devices(self, repo):
        """Should return all added devices."""
        devices_data = [
            DeviceCreate(
                hostname=f"device{i}",
                management_ip=f"10.0.0.{i}",
                platform=DevicePlatform.EOS,
                role=DeviceRole.LEAF,
                site="dc1",
            )
            for i in range(1, 4)
        ]

        for data in devices_data:
            repo.add(data)

        result = repo.get_all()

        assert len(result) == 3
        hostnames = {d.hostname for d in result}
        assert hostnames == {"device1", "device2", "device3"}


class TestUpdate:
    """Tests for update operation."""

    def test_update_single_field(self, repo, sample_device_data):
        """Should update only the specified field."""
        created = repo.add(sample_device_data)

        update = DeviceUpdate(hostname="spine1-updated")
        updated = repo.update(created.id, update)

        assert updated is not None
        assert updated.hostname == "spine1-updated"
        assert str(updated.management_ip) == "10.0.0.1"  # Unchanged

    def test_update_multiple_fields(self, repo, sample_device_data):
        """Should update multiple fields at once."""
        created = repo.add(sample_device_data)

        update = DeviceUpdate(
            hostname="new-spine",
            site="dc2",
        )
        updated = repo.update(created.id, update)

        assert updated.hostname == "new-spine"
        assert updated.site == "dc2"

    def test_update_changes_updated_at(self, repo, sample_device_data):
        """Update should change the updated_at timestamp."""
        created = repo.add(sample_device_data)
        original_updated_at = created.updated_at

        update = DeviceUpdate(site="dc2")
        updated = repo.update(created.id, update)

        assert updated.updated_at > original_updated_at

    def test_update_nonexistent_returns_none(self, repo):
        """Updating nonexistent device should return None."""
        update = DeviceUpdate(hostname="new-name")
        result = repo.update(uuid4(), update)

        assert result is None

    def test_update_to_duplicate_hostname_raises(self, repo):
        """Updating to an existing hostname should raise."""
        device1_data = DeviceCreate(
            hostname="device1",
            management_ip="10.0.0.1",
            platform=DevicePlatform.EOS,
            role=DeviceRole.LEAF,
            site="dc1",
        )
        device2_data = DeviceCreate(
            hostname="device2",
            management_ip="10.0.0.2",
            platform=DevicePlatform.EOS,
            role=DeviceRole.LEAF,
            site="dc1",
        )

        repo.add(device1_data)
        device2 = repo.add(device2_data)

        # Try to rename device2 to device1's hostname
        update = DeviceUpdate(hostname="device1")

        with pytest.raises(DuplicateDeviceError):
            repo.update(device2.id, update)


class TestDelete:
    """Tests for delete operation."""

    def test_delete_existing_device(self, repo, sample_device_data):
        """Should return True and remove the device."""
        created = repo.add(sample_device_data)

        result = repo.delete(created.id)

        assert result is True
        assert repo.get_by_id(created.id) is None

    def test_delete_nonexistent_returns_false(self, repo):
        """Should return False for unknown ID."""
        result = repo.delete(uuid4())

        assert result is False

    def test_delete_cleans_up_indexes(self, repo, sample_device_data):
        """Deleting should remove from hostname and IP indexes."""
        created = repo.add(sample_device_data)
        repo.delete(created.id)

        # Should be able to add same hostname and IP again
        new_device = repo.add(sample_device_data)
        assert new_device.hostname == "spine1"


class TestFilterBy:
    """Tests for filter_by operation."""

    @pytest.fixture
    def populated_repo(self, repo):
        """Repository with multiple devices for filtering tests."""
        devices = [
            DeviceCreate(
                hostname="spine1",
                management_ip="10.0.0.1",
                platform=DevicePlatform.EOS,
                role=DeviceRole.SPINE,
                site="dc1",
            ),
            DeviceCreate(
                hostname="spine2",
                management_ip="10.0.0.2",
                platform=DevicePlatform.EOS,
                role=DeviceRole.SPINE,
                site="dc2",
            ),
            DeviceCreate(
                hostname="leaf1",
                management_ip="10.0.0.3",
                platform=DevicePlatform.NXOS,
                role=DeviceRole.LEAF,
                site="dc1",
            ),
            DeviceCreate(
                hostname="leaf2",
                management_ip="10.0.0.4",
                platform=DevicePlatform.IOS_XE,
                role=DeviceRole.LEAF,
                site="dc1",
            ),
        ]

        for device_data in devices:
            repo.add(device_data)

        return repo

    def test_filter_by_platform(self, populated_repo):
        """Should return only devices matching platform."""
        results = populated_repo.filter_by(platform="eos")

        assert len(results) == 2
        assert all(d.platform == DevicePlatform.EOS for d in results)

    def test_filter_by_role(self, populated_repo):
        """Should return only devices matching role."""
        results = populated_repo.filter_by(role="spine")

        assert len(results) == 2
        assert all(d.role == DeviceRole.SPINE for d in results)

    def test_filter_by_site(self, populated_repo):
        """Should return only devices matching site."""
        results = populated_repo.filter_by(site="dc1")

        assert len(results) == 3
        assert all(d.site == "dc1" for d in results)

    def test_filter_by_multiple_criteria(self, populated_repo):
        """Should return devices matching ALL criteria."""
        results = populated_repo.filter_by(role="leaf", site="dc1")

        assert len(results) == 2
        assert all(d.role == DeviceRole.LEAF and d.site == "dc1" for d in results)

    def test_filter_no_matches_returns_empty(self, populated_repo):
        """Should return empty list when no matches."""
        results = populated_repo.filter_by(site="dc99")

        assert results == []

    def test_filter_no_criteria_returns_all(self, populated_repo):
        """Should return all devices when no criteria provided."""
        results = populated_repo.filter_by()

        assert len(results) == 4