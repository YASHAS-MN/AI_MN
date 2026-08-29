"""
identity — Persistent identity layer.

The identity is created once and never changes (except for version bumps).
It contains the entity's unique identifier, name, creation timestamp,
and current version string.
"""

import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from mind import storage

FILENAME = "identity.json"


@dataclass
class Identity:
    """Immutable identity of the artificial entity."""

    id: str
    name: str
    created_at: str  # ISO 8601
    version: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Identity":
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data["created_at"],
            version=data["version"],
        )


def _filepath(data_dir: str) -> str:
    return str(Path(data_dir) / FILENAME)


def load_or_create(data_dir: str, name: str = "Mind") -> Identity:
    """
    Load existing identity from disk, or create a new one.

    Args:
        data_dir: Path to the persistent data directory.
        name: Name for the entity (used only on first creation).

    Returns:
        The persistent Identity instance.
    """
    storage.ensure_dir(data_dir)
    data = storage.load(_filepath(data_dir))

    if data:
        return Identity.from_dict(data)

    # First creation.
    identity = Identity(
        id=str(uuid.uuid4()),
        name=name,
        created_at=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
    )
    save(data_dir, identity)
    return identity


def save(data_dir: str, identity: Identity) -> None:
    """Persist identity to disk."""
    storage.save(_filepath(data_dir), identity.to_dict())
