"""Events — the ledger of the simulation.

MINI-LESSON (event sourcing):
Think of a bank. Your balance is not a number someone edits in place; it is
the SUM of every transaction ever recorded. The ledger is the truth, the
balance is derived. Our sim works the same way: the world never mutates
silently — every change is recorded as an Event, and the world's state at
any tick can be rebuilt by replaying the log. This gives us replay,
debugging ("what happened at tick 512?"), and analysis for free.

Serialization detail that matters for determinism: json.dumps with
sort_keys=True and fixed separators guarantees the SAME event always
produces the SAME bytes. Python dicts preserve insertion order, but we
don't want byte-identity to depend on the order code happened to build a
payload in.
"""

from dataclasses import dataclass
from typing import Any
import json


@dataclass(frozen=True)  # frozen: an event is a historical fact, never edited
class Event:
    tick: int
    type: str
    payload: dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(
            {"tick": self.tick, "type": self.type, "payload": self.payload},
            sort_keys=True,
            separators=(",", ":"),
        )
