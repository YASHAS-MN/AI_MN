"""
state — Mutable internal state layer.

The internal state represents the entity's current condition. Unlike
identity, state is expected to change over time. It is persisted to disk
after every mutation.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from mind import storage

FILENAME = "state.json"


@dataclass
class InternalState:
    """Mutable internal state of the artificial entity."""

    current_state: str = "initialized"
    uncertainties: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    last_updated: str = ""  # ISO 8601

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "InternalState":
        return cls(
            current_state=data.get("current_state", "initialized"),
            uncertainties=data.get("uncertainties", []),
            open_questions=data.get("open_questions", []),
            last_updated=data.get("last_updated", ""),
        )

    def update(
        self,
        current_state: str | None = None,
        add_uncertainty: str | None = None,
        remove_uncertainty: str | None = None,
        add_question: str | None = None,
        remove_question: str | None = None,
    ) -> None:
        """
        Mutate internal state fields and refresh the timestamp.

        Each parameter is optional; only provided values are applied.
        """
        if current_state is not None:
            self.current_state = current_state
        if add_uncertainty is not None and add_uncertainty not in self.uncertainties:
            self.uncertainties.append(add_uncertainty)
        if remove_uncertainty is not None and remove_uncertainty in self.uncertainties:
            self.uncertainties.remove(remove_uncertainty)
        if add_question is not None and add_question not in self.open_questions:
            self.open_questions.append(add_question)
        if remove_question is not None and remove_question in self.open_questions:
            self.open_questions.remove(remove_question)
        self.last_updated = datetime.now(timezone.utc).isoformat()


def _filepath(data_dir: str) -> str:
    return str(Path(data_dir) / FILENAME)


def load_or_create(data_dir: str) -> InternalState:
    """
    Load existing state from disk, or create a new default state.
    """
    storage.ensure_dir(data_dir)
    data = storage.load(_filepath(data_dir))

    if data:
        return InternalState.from_dict(data)

    state = InternalState()
    state.last_updated = datetime.now(timezone.utc).isoformat()
    save(data_dir, state)
    return state


def save(data_dir: str, state: InternalState) -> None:
    """Persist state to disk."""
    storage.save(_filepath(data_dir), state.to_dict())
