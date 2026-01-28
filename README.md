# Network Device Inventory System

A Python library for managing network device inventory with support for multiple platforms and roles.

## Features

- **Device Management**: CRUD operations for network devices
- **Pydantic Validation**: Automatic validation of hostnames, IP addresses, platforms, and roles
- **Repository Pattern**: Pluggable storage backends (in-memory implementation included)
- **Immutable Models**: Thread-safe, frozen data models

## Supported Platforms

- Cisco IOS-XE
- Cisco IOS-XR
- Cisco NX-OS
- Arista EOS
- Juniper Junos

## Supported Roles

- Spine
- Leaf
- Border
- Core
- Access
- WAN

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from src.models import Device, DeviceCreate, DevicePlatform, DeviceRole
from src.repositories import InMemoryDeviceRepository

# Create a repository
repo = InMemoryDeviceRepository()

# Add a device
device_data = DeviceCreate(
    hostname="spine1",
    management_ip="10.0.0.1",
    platform=DevicePlatform.EOS,
    role=DeviceRole.SPINE,
    site="dc1",
)
device = repo.add(device_data)

# Query devices
all_devices = repo.get_all()
spines = repo.filter_by(role="spine")
dc1_devices = repo.filter_by(site="dc1")

# Update a device
from src.models import DeviceUpdate
update = DeviceUpdate(site="dc2")
updated_device = repo.update(device.id, update)

# Delete a device
repo.delete(device.id)
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=src
```

## Project Structure

```
├── src/
│   ├── models/
│   │   └── device.py       # Pydantic models for devices
│   └── repositories/
│       ├── base.py         # Abstract repository interface
│       ├── exceptions.py   # Custom exceptions
│       └── memory.py       # In-memory implementation
├── tests/
│   └── unit/
│       ├── test_models.py
│       └── test_repository_memory.py
└── pyproject.toml
```

## Requirements

- Python 3.12+
- Pydantic 2.0+
