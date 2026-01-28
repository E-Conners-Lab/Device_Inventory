"""
Unit tests for device models.

These tests verify:
1. Valid data creates valid models.
2. Invalid data raises appropriate errors
3. Immutability is enforced.
4. Default values work correctly
"""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.models.device import (
    Device,
    DeviceCreate,
    DevicePlatform,
    DeviceRole,
    DeviceUpdate,
)

class TestDevice:
    """ Tests for the Device model."""

    def test_create_valid_device(self):
        """A device with all valid fields should be created successfully."""
        device = Device (
            hostname="spine1",
            management_ip="10.0.0.1",
            platform=DevicePlatform.EOS,
            role=DeviceRole.SPINE,
            site="dc1"
        )

        assert device.hostname == "spine1"
        assert str(device.management_ip) == "10.0.0.1"
        assert device.platform == DevicePlatform.EOS
        assert device.role == DeviceRole.SPINE
        assert device.site == "dc1"


    def test_auto_generates_id(self):
        """Device should auto-generate a UUID if not provided."""
        device = Device(
            hostname="leaf1",
            management_ip="10.0.0.2",
            platform=DevicePlatform.EOS,
            role=DeviceRole.LEAF,
            site="dc1",
        )

        assert isinstance(device.id, UUID)

    def test_auto_generates_timestamps(self):
        """Device should auto-generate created_at and updated_at."""
        before = datetime.now()
        device = Device(
            hostname="leaf1",
            management_ip="10.0.0.2",
            platform=DevicePlatform.EOS,
            role=DeviceRole.LEAF,
            site="dc1",
        )

        after = datetime.now()

        assert before <= device.created_at <= after
        assert before <= device.updated_at <= after

    def test_rejects_empty_hostname(self):
        """Device should reject empty hostname."""
        with pytest.raises(ValidationError) as exc_info:
            Device (
                hostname="",
                management_ip="10.0.0.1",
                platform=DevicePlatform.EOS,
                role=DeviceRole.SPINE,
                site="dc1",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("hostname",) for e in errors)

    def test_rejects_invalid_ip(self):
        """Device should reject invalid IP addresses."""
        with pytest.raises(ValidationError) as exc_info:
            Device(
                hostname="spine1",
                management_ip="not-an-ip",
                platform=DevicePlatform.EOS,
                role=DeviceRole.SPINE,
                site="dc1",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] ==("management_ip",) for e in errors)

    def test_rejects_invalid_platform(self):
        """Device should reject platforms not in the enum."""
        with pytest.raises(ValidationError) as exc_info:
            Device(
                hostname="spine1",
                management_ip="10.0.0.1",
                platform="cisco_ios",  # Not a valid enum value
                role=DeviceRole.SPINE,
                site="dc1",
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("platform",) for e in errors)

    def test_immutability(self):
        """Device should be immutable (frozen)."""
        device = Device(
            hostname="spine1",
            management_ip="10.0.0.1",
            platform=DevicePlatform.EOS,
            role=DeviceRole.SPINE,
            site="dc1",
        )

        with pytest.raises(ValidationError):
            device.hostname = "new-name"


    def test_accepts_ipv6(self):
        """Device should accept valid IPv6 addresses."""
        device = Device(
            hostname="spine1",
            management_ip="2001:db8::1",
            platform=DevicePlatform.EOS,
            role=DeviceRole.SPINE,
            site="dc1",
        )

        assert str(device.management_ip) == "2001:db8::1"


class TestDeviceCreate:
    """Tests for the DeviceCreate schema."""

    def test_create_valid_schema(self):
        """DeviceCreate should accept all required fields."""
        create_data = DeviceCreate(
            hostname="spine1",
            management_ip="10.0.0.1",
            platform=DevicePlatform.EOS,
            role=DeviceRole.SPINE,
            site="dc1",
        )

        assert create_data.hostname == "spine1"

    def test_has_no_id_field(self):
        """DeviceCreate should not have an id field."""
        assert "id" not in DeviceCreate.model_fields

    def test_has_no_timestamp_fields(self):
        """DeviceCreate should not have timestamp fields."""
        assert "created_at" not in DeviceCreate.model_fields
        assert "updated_at" not in DeviceCreate.model_fields


class TestDeviceUpdate:
    """Test for the DeviceUpdate schema."""

    def test_all_fields_optional(self):
        """DeviceUpdate should allow empty initialization."""
        update = DeviceUpdate()

        assert update.hostname is None
        assert update.management_ip is None
        assert update.platform is None
        assert update.role is None
        assert update.site is None

    def test_partial_update(self):
        """DeviceUpdate should accept partial data."""
        update = DeviceUpdate(hostname="new-spine1")

        assert update.hostname == "new-spine1"
        assert update.management_ip is None  # Not provided

    def test_still_validates_provided_fields(self):
        """DeviceUpdate should validate fields that are provided."""
        with pytest.raises(ValidationError):
            DeviceUpdate(hostname="")  # Empty string should fail





