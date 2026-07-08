# PROGRESS

Read this at the START of every session; update it at the END. (See CLAUDE.md §6.)

## Current phase

**Phase 0 — deterministic core.**
Exit criterion: two same-seed runs produce byte-identical event logs, proven
locally (diff + sha256) and in CI.

Status: criterion demonstrated locally on Day 1 (seed 42, 401 events,
identical sha256). CI workflow written; needs a green run on GitHub to call
Phase 0 fully exited.

> NOTE: the full design doc (artificial-civilization-simulator-project-doc.md)
> is not in the repo yet. CLAUDE.md is the acting spec until it's added.

## Log

### Day 1 — 2026-07-08
- Housekeeping: created PROGRESS.md, renamed learning log to LEARNING_LOG.md,
  added .gitignore, removed stray `test` file, venv at .venv (pytest, pyyaml).
- Built the minimal deterministic core:
  - `engine/events.py` — frozen `Event(tick, type, payload)` with stable JSON
    serialization (sort_keys + fixed separators).
  - `engine/engine.py` — `Engine` with ONE seeded `random.Random`, agents
    random-walking a wrapping grid, every change emitted as an event.
  - `engine/run.py` — runs a yaml config from experiments/, writes JSONL to data/.
- `tests/test_determinism.py` — 3 tests, all passing.
- `.github/workflows/ci.yml` — pytest on every push, Python 3.12.
- Demonstrated exit criterion: two seed-42 runs, `diff` empty, sha256 equal
  (91ff053f…).

## Next

- Confirm CI is green on GitHub (completes Phase 0 exit).
- Add the design doc so Phases 1–8 have their real definitions.
- Then Phase 1 per the design doc.
