"""
Device domain models.

This module defines the core data structures for network devices.
We use Pydantic for automatic validation, serialization, and type safety.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, IPvAnyAddress


class DevicePlatform(str, Enum):
    """
    Supported network device platforms.

    Inheriting from both str and Enum gives us:
    - Type safety (can only user defined values)
    - String behavior (can compare with "ios_xe", serialize to JSON easily)
    """

    IOS_XE = "ios_xe"
    IOS_XR = "ios_xr"
    NXOS = "nxos"
    EOS = "eos"
    JUNOS ="junos"


class DeviceRole(str, Enum):
    """
    Network device roles in the topology.

    Roles help categorize devices for filtering and automation targeting.
    """

    SPINE = "spine"
    LEAF ="leaf"
    BORDER = "border"
    CORE = "core"
    ACCESS = "access"
    WAN = "wan"



class Device(BaseModel):
    """
    Represents a network device in inventory.

    This is an immutable data transfer object (DTO). Pydantic models are
    immutable by default in v2, which prevents accidental mutations and
    makes the code easier to reason about.

    Attributes:
        id: Unique identifier, auto-generated if not provided
        hostname: Device hostname (required, must be non-empty)
        management_ip: Management IP address (validated by Pydantic)
        platform: Network OS platform
        role: Device's role in the network topology
        site: Physical or logical site identifier
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last modified
    """

    id: UUID = Field(default_factory=uuid4)
    hostname: str = Field(..., min_length=1, max_length=253)
    management_ip: IPvAnyAddress
    platform: DevicePlatform
    role: DeviceRole
    site: str = Field(..., min_length=1, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {
        "frozen": True, # Makes instances immutable
        "str_strip_whitespace": True, # Strips whitespace from field strings
    }


class DeviceCreate(BaseModel):
    """
    Schema for creating a new device.

    This is separate from Device because:
    1. We don't want users providing, id, created_at, updated_at
    2. It clearly documents what fields are required for creation
    3. It follows the "Parse, don't validate" principle

    The service layer will convert this to a full Device.
    """

    hostname: str = Field(..., min_length=1, max_length=253)
    management_ip: IPvAnyAddress
    platform: DevicePlatform
    role: DeviceRole
    site: str = Field(..., min_length=1, max_length=100)


class DeviceUpdate(BaseModel):
    """
    Schema for updating an existing device.

    All fields are optional - only provided field will be updated.
    This pattern is called a "Partial Update" or "Patch" schema.
    """

    hostname: Optional [str] = Field(None, min_length=1, max_length=253)
    management_ip: Optional[IPvAnyAddress] = None
    platform: Optional[DevicePlatform] = None
    role: Optional[DeviceRole] = None
    site: Optional[str] = Field(None, min_length=1, max_length=100)

