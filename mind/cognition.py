"""
cognition — Minimal input→output processing.

This module is the bridge between input and output. In V0, it is a
deterministic stub that acknowledges receipt, records the input as an
experience, and updates the entity's state.

Future versions replace the body of process() with actual reasoning
(LLM, rule engine, etc.) without changing the function signature.
"""

from mind.identity import Identity
from mind.state import InternalState
from mind.memory import MemoryStore


def process(
    input_text: str,
    identity: Identity,
    state: InternalState,
    memory: MemoryStore,
) -> str:
    """
    Process an input and produce an output.

    This is the sole cognitive interface. Everything the entity "thinks"
    passes through this function.

    Args:
        input_text: The raw input string.
        identity: The entity's persistent identity.
        state: The entity's mutable internal state.
        memory: The entity's memory store.

    Returns:
        A response string.
    """
    # 1. Record the input as an experience.
    experience = memory.record(
        content=input_text,
        importance=0.5,
        source="input",
    )

    # 2. Update internal state to reflect that input was received.
    state.update(current_state="received_input")

    # 3. Produce a minimal deterministic response.
    response = (
        f"[{identity.name}] Input received.\n"
        f"  Experience recorded: {experience.id}\n"
        f"  State: {state.current_state}\n"
        f"  Total memories: {memory.count()}"
    )

    return response
