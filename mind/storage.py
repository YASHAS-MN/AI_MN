"""
storage — JSON file persistence utility.

Provides atomic read/write of JSON files. This is the only module that
touches the filesystem directly. To migrate to a different storage backend
(SQLite, YAML, etc.), replace this module and keep the same interface.
"""

import json
import os
import tempfile
from pathlib import Path


def ensure_dir(data_dir: str) -> None:
    """Create the data directory if it does not exist."""
    Path(data_dir).mkdir(parents=True, exist_ok=True)


def load(filepath: str) -> dict:
    """
    Load a JSON file and return its contents as a dict.
    Returns an empty dict if the file does not exist.
    """
    path = Path(filepath)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(filepath: str, data: dict) -> None:
    """
    Atomically write data to a JSON file.

    Writes to a temporary file first, then renames it to the target path.
    This prevents corruption if the process is interrupted mid-write.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temp file in the same directory, then replace.
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=".mind_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # On Windows, os.replace is atomic if src and dst are on the same volume.
        os.replace(tmp_path, str(path))
    except BaseException:
        # Clean up the temp file on failure.
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
