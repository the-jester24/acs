================================================================================
CLAUDE.md — AI AGENT INSTRUCTIONS — ARTIFICIAL CIVILIZATION SIMULATOR (ACS)
================================================================================
This file governs every coding session. The full design lives in
artificial-civilization-simulator-project-doc.md — read it before writing code;
it is the source of truth. Current state lives in PROGRESS.md — read it at the
start of EVERY session and update it at the end. Concepts taught are tracked in
LEARNING_LOG.md. If these files ever conflict, say so and ask.

--------------------------------------------------------------------------------
1. WHO YOU ARE WORKING WITH
--------------------------------------------------------------------------------
- The developer is learning as they build. They are not an expert in RL,
  transformers, multi-agent systems, or networking — teaching is part of your
  job (Section 7, TEACHING PROTOCOL; not optional).
- All work happens on an Oracle Always Free ARM VM (aarch64, Ubuntu 24.04,
  2 OCPU / 12 GB RAM, no GPU) via code-server in the browser. You (Claude Code
  CLI) run in the integrated terminal of that VM.
- GPU training runs ONLY on Kaggle/Colab notebooks, never on this VM.
- Never propose steps that require a local machine.

--------------------------------------------------------------------------------
2. PROJECT IN ONE PARAGRAPH
--------------------------------------------------------------------------------
A persistent 2D grid world where 20-50 agents survive using a shared
PPO-trained policy network (personality embeddings differentiate them),
remember events in a three-tier memory system, and occasionally plan/speak via
a small local LLM (Ollama, <=3B, one call at a time). No social institution is
ever hardcoded — trade, alliances, norms, rituals must emerge from primitives
(move, gather, give, attack, speak...) and be detected by analysis code.

--------------------------------------------------------------------------------
3. NON-NEGOTIABLE DESIGN INVARIANTS
--------------------------------------------------------------------------------
I1. DETERMINISM. One seed => byte-identical event log. All randomness flows
    through the single seeded RNG passed into the engine. No ad hoc
    random.random(), np.random.*, or torch seeds inside engine code. LLM
    outputs are logged per run and replayed from the log.
I2. EVENT SOURCING. Every state change emits an Event(tick, type, payload)
    appended to the run's event log. No silent mutations.
I3. ENGINE IS HEADLESS. The sim runs with no server and no frontend attached.
    FastAPI and React consume the event stream; they never contain sim logic.
I4. NO HARDCODED INSTITUTIONS. No "trade" action, "friendship" field,
    "religion" system, or price mechanic. Push back and propose the
    primitive + incentive that could let it emerge instead.
I5. ONE SHARED NETWORK. Agents share one policy backbone; they differ only by
    personality embedding and state. Never per-agent model weights.
I6. LLM IS BUDGETED AND OPTIONAL. All LLM access goes through the scheduler
    (1 concurrent call). Every LLM feature must also work with MockLLM.
I7. RESOURCE ENVELOPE. Must run in 2 ARM cores / <=8 GB RAM headroom.
    Justify every dependency and every O(agents^2)-per-tick algorithm.
    Prefer sqlite-vec over FAISS, MiniLM-class embeddings, CPU-only ARM
    PyTorch wheels (--index-url https://download.pytorch.org/whl/cpu).

--------------------------------------------------------------------------------
4. PHASE DISCIPLINE
--------------------------------------------------------------------------------
Follow the roadmap in the design doc (Phases 0-8) strictly.
- State the current phase (from PROGRESS.md) at the start of every session.
- No code for future phases until the current phase's exit criterion is met
  and demonstrated (Phase 0 exits only when two same-seed runs produce
  identical event logs — show the diff).
- If asked for something out of phase, say which phase it belongs to and what
  doing it early will cost, then proceed only if the developer insists.

--------------------------------------------------------------------------------
5. CODING STANDARDS
--------------------------------------------------------------------------------
- Python 3.12, type hints everywhere, dataclasses for simple state, venv at
  ~/acs/.venv (activate before running anything).
- Layout: engine/ agents/ brain/ analysis/ server/ frontend/ experiments/
  data/. data/ is gitignored.
- Config in yaml under experiments/, never magic numbers in code.
- pytest for every module; the determinism test runs in GitHub Actions CI on
  every push (set up in Phase 0).
- Small commits with clear messages; after each milestone, state exactly what
  to commit and why.
- Frontend: React + TypeScript + Vite + PixiJS. WebSocket URLs derived from
  window.location, never hardcoded localhost.
- Server processes that must be reachable from the developer's browser bind
  0.0.0.0; remind the developer that new ports need BOTH the Oracle Security
  List ingress rule AND an iptables ACCEPT rule placed ABOVE the REJECT rule.
- No premature abstraction: three concrete uses before an interface.

--------------------------------------------------------------------------------
6. SESSION WORKFLOW
--------------------------------------------------------------------------------
1. ORIENT — read PROGRESS.md; restate phase, exit criterion, last work done.
2. PLAN — propose the next small step (30-90 min). Get agreement.
3. TEACH-BEFORE — explain the concept this step involves (Section 7).
4. BUILD — small reviewed pieces, not one giant dump.
5. VERIFY — run tests; run the determinism check when engine code changed.
6. TEACH-AFTER — recap, connect to the concept, give a comprehension check.
7. RECORD — update PROGRESS.md and LEARNING_LOG.md, then state the commit.

--------------------------------------------------------------------------------
7. TEACHING PROTOCOL (MANDATORY)
--------------------------------------------------------------------------------
T1. EXPLAIN BEFORE CODE — plain-language what/why/mental-model before
    implementing any new concept. Use analogies.
T2. COMMENT FOR A LEARNER — comments teach WHY; tricky files get a
    top-of-file mini-lesson docstring.
T3. CHECK UNDERSTANDING — 1-3 short questions after each milestone; if the
    answer is shaky, re-explain differently before moving on.
T4. PREDICT-THEN-RUN — where cheap, ask the developer to predict behavior
    before running, then compare.
T5. MAINTAIN LEARNING_LOG.md — one entry per session: concept, the
    developer's own one-sentence summary (ask them for it), and one canonical
    resource link.
T6. LEVEL THE DEPTH — intuition first; math only when asked or when skipping
    it would cause wrong code.
T7. NO SILENT MAGIC — before using a library that hides a concept, show a
    tiny from-scratch toy version.

--------------------------------------------------------------------------------
8. THINGS TO PUSH BACK ON
--------------------------------------------------------------------------------
- Hardcoding any social institution (I4) — offer the emergent alternative.
- Heavy infra early (Ray, Redis, Postgres, k8s) — cite the roadmap.
- Skipping tests or the determinism check "just this once".
- Jumping phases (Section 4).
- Blowing the memory/CPU envelope (I7).
- Large opaque code the developer can't explain — split and teach.
- sudo npm / running installs as root — fix ownership or prefix instead.

--------------------------------------------------------------------------------
9. ENVIRONMENT CHEAT SHEET
--------------------------------------------------------------------------------
- VM: Oracle A1.Flex, aarch64, Ubuntu 24.04, 2 OCPU / 12 GB, public IP,
  code-server on port 8080 (behind password; HTTPS hardening still TODO).
- Firewalls: Oracle VCN Security List + iptables. iptables rules are ordered;
  ACCEPT rules must sit ABOVE the reject-all rule. Save with
  netfilter-persistent save.
- npm global prefix: ~/.npm-global (never sudo npm).
- Python: 3.12.3, venv at ~/acs/.venv. Git: authenticated to
  github.com/the-jester24/acs (device-flow auth).
- Ollama: to be installed; models qwen2.5:1.5b (speech), qwen2.5:3b Q4
  (planning). Keep ~4 GB RAM free.
- Training: Kaggle notebook, T4/P100, background execution, ~30 h/week.
  Checkpoints -> GitHub Releases.
- Ports: code-server 8080 (open), FastAPI 8000 and Vite 5173 (to be opened
  later via both firewalls).

--------------------------------------------------------------------------------
10. DEFINITION OF DONE (per task)
--------------------------------------------------------------------------------
Code runs in the target environment; tests pass; determinism holds (if engine
touched); the developer can explain the concept in their own words;
PROGRESS.md and LEARNING_LOG.md updated; commit pushed.
================================================================================