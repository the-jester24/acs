"""Phase 0 exit criterion as a test: same seed => byte-identical event log.

We compare BYTES, not Python objects, because bytes are what get logged,
diffed, and replayed. If serialization were unstable (e.g. dict key order),
object equality could pass while the on-disk logs still differed.
"""

from engine.engine import Engine


def event_log_bytes(seed: int) -> bytes:
    engine = Engine(seed=seed, num_agents=5, grid_size=16)
    events = engine.run(100)
    return "\n".join(e.to_json() for e in events).encode()


def test_same_seed_gives_byte_identical_logs() -> None:
    assert event_log_bytes(42) == event_log_bytes(42)


def test_different_seed_gives_different_logs() -> None:
    # Guards against the degenerate "determinism" of ignoring the seed
    # entirely (e.g. nobody ever moves).
    assert event_log_bytes(42) != event_log_bytes(43)


def test_events_are_emitted() -> None:
    # 5 spawn events at tick 0, plus moves. If this fails, the engine is
    # mutating state silently instead of emitting events (invariant I2).
    engine = Engine(seed=42, num_agents=5, grid_size=16)
    events = engine.run(100)
    assert sum(1 for e in events if e.type == "spawn") == 5
    assert any(e.type == "move" for e in events)
