"""
test_v0.py — Verification script for all 7 V0 completion criteria.

Runs a self-contained test sequence that validates:
  1. The entity can be created.
  2. It retains the same identity after restarting the program.
  3. Its internal state persists after restarting.
  4. It can record an experience.
  5. The experience remains available after restarting.
  6. The entity can receive an input and produce an output.
  7. The entity can be moved to another machine (simulated by copying data dir).

Uses only the standard library. No test framework required.
"""

import os
import sys
import shutil
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(SCRIPT_DIR, "test_mind_data")


def cleanup():
    """Remove the test data directory."""
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)


def run_tests():
    passed = 0
    failed = 0
    total = 7

    def check(criterion: int, description: str, condition: bool):
        nonlocal passed, failed
        status = "PASS" if condition else "FAIL"
        print(f"  [{status}] Criterion {criterion}: {description}")
        if condition:
            passed += 1
        else:
            failed += 1

    print("\n=== V0 Completion Criteria Tests ===\n")

    # --- Setup: clean slate ---
    cleanup()

    # --- Criterion 1: The entity can be created ---
    from mind.identity import load_or_create as load_identity
    from mind.state import load_or_create as load_state, save as save_state
    from mind.memory import MemoryStore

    identity = load_identity(TEST_DATA_DIR, name="TestMind")
    state = load_state(TEST_DATA_DIR)
    memory = MemoryStore(TEST_DATA_DIR)

    identity_file = os.path.join(TEST_DATA_DIR, "identity.json")
    state_file = os.path.join(TEST_DATA_DIR, "state.json")

    check(1, "Entity can be created",
          os.path.exists(identity_file)
          and os.path.exists(state_file)
          and identity.name == "TestMind"
          and identity.id != "")

    # --- Criterion 2: Same identity after restart ---
    original_id = identity.id
    original_name = identity.name
    original_created = identity.created_at

    # Simulate restart: reload from disk.
    identity2 = load_identity(TEST_DATA_DIR, name="ShouldBeIgnored")

    check(2, "Retains same identity after restart",
          identity2.id == original_id
          and identity2.name == original_name
          and identity2.created_at == original_created)

    # --- Criterion 3: Internal state persists after restart ---
    state.update(current_state="testing", add_uncertainty="Is this working?")
    save_state(TEST_DATA_DIR, state)

    # Simulate restart: reload from disk.
    state2 = load_state(TEST_DATA_DIR)

    check(3, "Internal state persists after restart",
          state2.current_state == "testing"
          and "Is this working?" in state2.uncertainties)

    # --- Criterion 4: Can record an experience ---
    experience = memory.record(
        content="This is a test experience.",
        importance=0.8,
        source="test",
    )

    check(4, "Can record an experience",
          experience.id != ""
          and experience.content == "This is a test experience."
          and experience.importance == 0.8
          and experience.source == "test")

    # --- Criterion 5: Experience available after restart ---
    exp_id = experience.id

    # Simulate restart: create a new MemoryStore from disk.
    memory2 = MemoryStore(TEST_DATA_DIR)
    reloaded = memory2.get_by_id(exp_id)

    check(5, "Experience remains available after restart",
          reloaded is not None
          and reloaded.content == "This is a test experience."
          and reloaded.importance == 0.8)

    # --- Criterion 6: Can receive input and produce output ---
    from mind.cognition import process

    output = process("Hello, mind.", identity2, state2, memory2)
    save_state(TEST_DATA_DIR, state2)

    check(6, "Can receive input and produce output",
          isinstance(output, str)
          and len(output) > 0
          and "TestMind" in output)

    # --- Criterion 7: Portable — can be moved to another location ---
    tmp_dir = tempfile.mkdtemp(prefix="mind_portable_")
    portable_data = os.path.join(tmp_dir, "mind_data")
    shutil.copytree(TEST_DATA_DIR, portable_data)

    identity3 = load_identity(portable_data)
    state3 = load_state(portable_data)
    memory3 = MemoryStore(portable_data)

    check(7, "Entity portable to another location",
          identity3.id == original_id
          and state3.current_state == state2.current_state
          and memory3.count() == memory2.count())

    # Cleanup portable copy.
    shutil.rmtree(tmp_dir)

    # --- Summary ---
    print(f"\n  Results: {passed}/{total} passed, {failed}/{total} failed")

    if failed == 0:
        print("\n  [OK] All V0 completion criteria satisfied.\n")
    else:
        print(f"\n  [FAILED] {failed} criterion/criteria not met.\n")

    # Cleanup test data.
    cleanup()

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
