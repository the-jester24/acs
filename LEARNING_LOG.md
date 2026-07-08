# LEARNING LOG

## Day 1 — determinism, seeded RNG, event sourcing
- **Seeded RNG:** a PRNG is a predictable formula, not dice — the seed is the
  starting point, and the same seed replays the exact same "random" sequence
  on any machine. Like a deck shuffled with seed 42: always the same order.
- **Why ONE shared RNG object:** any stray `random.random()` or `time()` call
  pulls from hidden state and breaks replay. All randomness flows through the
  single `random.Random(seed)` handed to the engine (invariant I1).
- **Iteration order is part of determinism:** agents are processed in sorted
  id order every tick — if the order varied, agents would draw different
  numbers from the shared RNG stream and same-seed logs would diverge.
- **Event sourcing:** state is never edited in place; every change is an
  appended `Event(tick, type, payload)`, like a bank ledger where the balance
  is derived from transactions. Replay the log => rebuild any past state.
- **Byte-identity needs stable serialization:** `json.dumps(sort_keys=True,
  separators=(",",":"))` so the same event always produces the same bytes.
- **pytest gotcha:** the repo root isn't on `sys.path` during collection;
  fix with `pythonpath = ["."]` in pyproject.toml.
- In short: one seed gives one exact history because every "random" choice
  is just the next number from a formula the seed fully determines — so the
  same seed replays the same choices, ticks, and events, byte for byte.
- Resource: Martin Fowler, "Event Sourcing" —
  https://martinfowler.com/eaaDev/EventSourcing.html

## Day 0 — cloud & networking fundamentals
- **VM / cloud server:** a rented slice of a data-center machine that runs
  24/7 independently of my laptop.
- **Public vs private IP:** public = reachable from the internet; private =
  only inside the cloud network.
- **SSH key pairs:** public key on server, private key with me; proves
  identity without sending a password. Losing the private key = losing access.
- **bind-addr:** 127.0.0.1 = only the machine itself can connect; 0.0.0.0 =
  reachable from outside. My words: "with the default, only the VM can reach
  it; with 0.0.0.0 my laptop can too."
- **Two-layer firewalls:** Oracle Security List (outer gate) AND iptables
  (inner gate) must BOTH allow a port.
- **iptables ordering:** rules are read top-down, first match wins. My words:
  "the 5th rule rejected everything so the 6th (allow 8080) never got
  reached; moving allow above reject fixed it."
- **Hang vs refuse:** silent DROP makes connections hang; REJECT fails fast —
  which one you see hints at which gate is blocking.
- **npm EACCES / least privilege:** don't sudo your way past permissions;
  point npm's prefix at a folder you own. Same principle as minimal token
  scopes (only `repo`).
- Resource: Julia Evans' networking zines (wizardzines.com) for
  firewalls/ports intuition.