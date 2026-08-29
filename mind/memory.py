"""
memory — Experience recording and retrieval.

Each experience is a discrete record of something the entity has perceived,
processed, or been told. Memories are append-only in V0 (no deletion or
editing). No indexing or semantic search — just linear storage.
"""

import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from mind import storage

FILENAME = "memories.json"


@dataclass
class Experience:
    """A single recorded experience."""

    id: str
    content: str
    timestamp: str  # ISO 8601
    importance: float  # 0.0 to 1.0
    source: str  # e.g. "input", "internal", "observation"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Experience":
        return cls(
            id=data["id"],
            content=data["content"],
            timestamp=data["timestamp"],
            importance=float(data["importance"]),
            source=data["source"],
        )


class MemoryStore:
    """
    Append-only store of experiences backed by a single JSON file.

    The entire memory is held in-memory as a list and flushed to disk
    on every write. This is intentionally simple — V0 does not need
    streaming, pagination, or indexing.
    """

    def __init__(self, data_dir: str) -> None:
        self._data_dir = data_dir
        self._filepath = str(Path(data_dir) / FILENAME)
        self._experiences: List[Experience] = []
        self._load()

    def _load(self) -> None:
        """Load experiences from disk."""
        storage.ensure_dir(self._data_dir)
        data = storage.load(self._filepath)
        raw_list = data.get("experiences", [])
        self._experiences = [Experience.from_dict(e) for e in raw_list]

    def _save(self) -> None:
        """Persist all experiences to disk."""
        data = {"experiences": [e.to_dict() for e in self._experiences]}
        storage.save(self._filepath, data)

    def record(
        self, content: str, importance: float = 0.5, source: str = "input"
    ) -> Experience:
        """
        Record a new experience and persist it.

        Args:
            content: What happened or what was received.
            importance: How significant this experience is (0.0–1.0).
            source: Origin of the experience (e.g. "input", "internal").

        Returns:
            The newly created Experience.
        """
        experience = Experience(
            id=str(uuid.uuid4()),
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            importance=max(0.0, min(1.0, importance)),
            source=source,
        )
        self._experiences.append(experience)
        self._save()
        return experience

    def get_all(self) -> List[Experience]:
        """Return all recorded experiences (oldest first)."""
        return list(self._experiences)

    def get_by_id(self, experience_id: str) -> Optional[Experience]:
        """Find an experience by its unique ID, or return None."""
        for exp in self._experiences:
            if exp.id == experience_id:
                return exp
        return None

    def count(self) -> int:
        """Return the total number of recorded experiences."""
        return len(self._experiences)
