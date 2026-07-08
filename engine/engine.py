"""The engine core — a deterministic tick loop.

MINI-LESSON (determinism & seeded RNG):
A pseudo-random number generator is not magic dice — it is a completely
predictable formula that scrambles a starting number (the SEED) into a
sequence that merely LOOKS random. Same seed => same sequence, forever,
on any machine. Think of it as a pre-shuffled deck of cards: shuffling
with seed 42 always yields the exact same deck order.

That is why invariant I1 demands ONE Random object, created from the seed,
passed everywhere. If any code called random.random() (the global RNG) or
time(), the sequence would depend on hidden state and replay would break.

Second determinism trap: ITERATION ORDER. We always loop over agents in
sorted id order. If agent order varied between runs, each agent would pull
different numbers from the shared RNG stream and the logs would diverge —
even with the same seed.

The engine is headless (invariant I3): no server, no UI, just
state + tick() + an event log.
"""

import random

from engine.events import Event

# The 4 cardinal moves plus "stay". Order is fixed — part of determinism:
# rng.choice indexes into this tuple, so reordering it changes every run.
MOVES: tuple[tuple[int, int], ...] = ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0))


class Engine:
    def __init__(self, seed: int, num_agents: int, grid_size: int) -> None:
        self.rng = random.Random(seed)  # the ONLY source of randomness (I1)
        self.grid_size = grid_size
        self.tick_count = 0
        self.events: list[Event] = []

        # Deterministic spawn: agents placed in id order from the seeded RNG.
        self.positions: dict[int, tuple[int, int]] = {}
        for agent_id in range(num_agents):
            pos = (self.rng.randrange(grid_size), self.rng.randrange(grid_size))
            self.positions[agent_id] = pos
            self._emit("spawn", {"agent": agent_id, "pos": list(pos)})

    def _emit(self, type: str, payload: dict) -> None:
        self.events.append(Event(self.tick_count, type, payload))

    def tick(self) -> None:
        self.tick_count += 1
        for agent_id in sorted(self.positions):  # fixed order (see mini-lesson)
            x, y = self.positions[agent_id]
            dx, dy = self.rng.choice(MOVES)
            # The grid wraps around like Pac-Man (a torus): stepping off the
            # right edge re-enters on the left. Modulo does the wrapping.
            new = ((x + dx) % self.grid_size, (y + dy) % self.grid_size)
            if new != (x, y):
                self.positions[agent_id] = new
                self._emit("move", {"agent": agent_id, "from": [x, y], "to": list(new)})

    def run(self, ticks: int) -> list[Event]:
        for _ in range(ticks):
            self.tick()
        return self.events
