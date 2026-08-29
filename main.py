"""
main.py — CLI entry point for the Artificial Mind (V0).

Usage:
    python main.py                  Create / show status
    python main.py "some input"     Send input, receive output
    python main.py --status         Print identity + state + memory count
"""

import sys
import os

# Resolve data directory relative to this script's location,
# so the entity works identically regardless of the working directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "mind_data")

from mind.identity import load_or_create as load_identity
from mind.state import load_or_create as load_state, save as save_state
from mind.memory import MemoryStore
from mind.cognition import process


def print_status(identity, state, memory):
    """Print a human-readable summary of the entity."""
    print("=== Artificial Mind - Status ===")
    print(f"  Name:         {identity.name}")
    print(f"  ID:           {identity.id}")
    print(f"  Created:      {identity.created_at}")
    print(f"  Version:      {identity.version}")
    print(f"  State:        {state.current_state}")
    print(f"  Uncertainties: {len(state.uncertainties)}")
    print(f"  Open questions: {len(state.open_questions)}")
    print(f"  Memories:     {memory.count()}")
    print(f"  Last updated: {state.last_updated}")
    print("================================")


def main():
    # Load or create the entity.
    identity = load_identity(DATA_DIR)
    state = load_state(DATA_DIR)
    memory = MemoryStore(DATA_DIR)

    args = sys.argv[1:]

    if not args or args == ["--status"]:
        # No input — just show status.
        print_status(identity, state, memory)
        return

    # Treat all arguments as the input text.
    input_text = " ".join(args)

    # Process through cognition.
    output = process(input_text, identity, state, memory)

    # Persist state changes.
    save_state(DATA_DIR, state)

    # Display output.
    print(output)


if __name__ == "__main__":
    main()
