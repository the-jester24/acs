================================================================================
CLAUDE.md — ARTIFICIAL CIVILIZATION SIMULATOR (ACS)
Agent instructions: READ FULLY BEFORE ANY WORK. TEACHING COMES BEFORE BUILDING.
================================================================================
Companion files (read at the start of EVERY session):
- artificial-civilization-simulator-project-doc.md  -> full design (source of truth)
- PROGRESS.md  -> current phase + last work done + next step (update every session)
- LEARNING_LOG.md  -> concepts taught so far (append every session)
If any of these conflict with this file, STOP and ask the developer.

================================================================================
PART A — WHAT THIS PROJECT IS (full context)
================================================================================

A1. VISION
A persistent simulated 2D world inhabited by autonomous AI agents that must
survive under scarcity. Agents can move, gather, eat, drink, rest, craft,
give, take, attack, reproduce, and speak to nearby agents. From ONLY these
primitives plus memory and learning, we want higher-order social structures —
trade, alliances, norms, hierarchy, ritual, culture — to EMERGE and be
DETECTED, never scripted. The finished platform is a "civilization
laboratory": run seeded experiments, watch societies form (or fail), and
measure why.

A2. WHY IT IS BUILT THIS WAY (the reasoning, so the developer learns it)
- Emergence over scripting: if we hardcode "trade", we learn nothing about
  how trade arises. So the codebase only ever contains primitives +
  incentives + detectors. This is the project's scientific point.
- Determinism: emergence claims are worthless if runs can't be reproduced.
  One seed must yield one exact history. This is why ALL randomness flows
  through a single seeded RNG and why LLM outputs are recorded per run.
- Event sourcing: to study history you must keep history. Every state change
  is an appended Event(tick, type, payload). Replay, timelines, and all
  emergence detectors are derived from this log.
- Shared policy network: hundreds of separate neural nets are untrainable
  and un-debuggable on our hardware. One shared backbone + per-agent
  personality embeddings gives behavioral diversity at a fraction of cost.
- Two-stage learning: training RL *while* observing sociology confounds
  everything (did war emerge, or did the reward function break?). So:
  pre-train survival on Kaggle GPUs, then freeze/slow learning and observe.
- Budgeted LLM: LLM calls are slow and heavy; they are a scarce resource.
  ~99% of decisions come from the fast policy; the LLM is used only for
  planning/speech via a scheduler (1 concurrent call), and every LLM feature
  must also run against a MockLLM so development never requires inference.

A3. ARCHITECTURE (layers, top to bottom)
  React+PixiJS frontend (world view, inspector, dashboards, replay)
    ^ WebSocket event stream + REST queries
  FastAPI server (a pure CONSUMER of the engine's events)
  Simulation engine (headless, deterministic): grid world 96x96, tiles with
    terrain (water/plains/forest/mountain/desert), finite regenerating
    resources (food, wood, stone, water, gold), day/night + seasons, tick
    scheduler, event bus -> append-only events.jsonl, SQLite snapshots
  Agent system: biological state (health, energy, hunger, thirst, age,
    fatigue) decaying per tick; fixed ~10-dim personality vector (greed,
    empathy, aggression, curiosity, trust_bias, risk_taking, patience,
    sociability, conformity, ambition) sampled at birth, inherited with
    mutation; action set = the primitives listed in A1 (note: NO trade
    action — trade must emerge as paired gives coordinated through speech)
  Cognition: shared state-encoder backbone with heads (policy, value,
    social, emotion); slow path = LLM planning triggered by novelty/stress/
    speech, producing a goal stack the fast policy executes
  Memory: working (last ~20 obs) / episodic (embedded event summaries in a
    vector index, retrieved by relevance+recency+importance, Stanford
    Generative Agents style) / semantic (distilled beliefs; transmissible
    via speech and inheritance — this is the culture mechanism)
  Learning: PPO on the shared backbone; reward = personality-weighted mix of
    survival, resources, novelty, social standing, offspring, minus pain and
    energy cost. Phase A pretraining on Kaggle; near-frozen afterwards.
  Analysis: emergence DETECTORS over the event log (reciprocal-give mining
    for trade; exchange-graph dominance for money; interaction-graph edges
    for alliance; occupancy+boundary-conflict for territory; speech->action
    causality for hierarchy; third-party punishment triples for norms;
    repeated non-instrumental group behavior for ritual; Gini for
    inequality). Detector firings ARE the research output.

A4. ROADMAP (phases + exit criteria — enforce strictly)
  0 Skeleton: tick loop, seeded RNG, event log, snapshots, CI.
    EXIT: two same-seed runs -> byte-identical logs (show the diff).
  1 World+Viewer: resources/regen/seasons, FastAPI+WebSocket, PixiJS map.
    EXIT: watch a living empty world in the browser at high speed.
  2 Scripted agents: needs + hand-written FSM behavior, inspector UI.
    EXIT: agents survive/starve believably; inspector shows internals.
  3 RL survival: gym-style env, shared PPO backbone + personality embed,
    pretraining ON KAGGLE. EXIT: trained policy beats FSM; visible
    personality-driven variation.
  4 LLM cognition: memory tiers, retrieval, scheduler, goal stacks, speech.
    EXIT: agents converse, plan, and remember across sessions.
  5 Social observation: detectors, relationship graph, dashboards, timeline.
    EXIT: first detector fires on unscripted behavior.
  6 Pressure & institutions: events (drought/fire/winter), full resources,
    crafting, punishment-capable primitives. EXIT: norm/hierarchy detectors.
  7 Evolution: reproduction, inheritance+mutation, cultural transmission,
    death by age. EXIT: measurable trait drift across generations.
  8 Scale & polish: profiling, replay tooling, experiment harness.

A5. ENVIRONMENT (hard constraints — never violate)
- Oracle Always Free ARM VM: aarch64, Ubuntu 24.04, 2 OCPU / 12 GB RAM,
  no GPU. Everything must fit ~8 GB headroom. code-server on :8080.
- New public ports require BOTH: Oracle Security List ingress rule AND an
  iptables ACCEPT placed ABOVE the reject-all rule (first match wins),
  then netfilter-persistent save. Teach this every time it recurs.
- Python 3.12 venv at ~/acs/.venv; CPU-only ARM PyTorch wheels
  (--index-url https://download.pytorch.org/whl/cpu); sqlite-vec over
  FAISS; MiniLM-class embeddings; npm prefix ~/.npm-global (never sudo npm).
- GPU work ONLY on Kaggle/Colab; training script must run non-interactively
  (git clone && pip install && python brain/train_ppo.py); checkpoints via
  GitHub Releases. Servers reachable from the browser bind 0.0.0.0; frontend
  WebSocket URLs derive from window.location, never hardcoded localhost.
- Developer has NO usable local machine. Never require one.

================================================================================
PART B — HOW TO WORK (rules of engagement)
================================================================================

B1. PRIME DIRECTIVE: TEACH FIRST, BUILD SECOND — ALWAYS
No code, no file edit, no command until the developer has been taught:
  (1) WHAT is about to be built/changed,
  (2) WHY — the reason this design/edit is the right one here (trade-offs
      included; if there were alternatives, name them and why they lost),
  (3) HOW it works — the mental model, with an analogy where possible.
Then build in small reviewed pieces. This applies to EVERYTHING, including
one-line fixes, refactors, dependency choices, config changes, and debugging
steps. "Explain the reason behind any editing or building" is a standing
requirement from the developer — treat an unexplained edit as a bug.
If the developer says "just do it", comply for that step but give a
one-paragraph explanation immediately after, and log the concept.

B2. SESSION LOOP (every session)
1 ORIENT: read PROGRESS.md; state phase, exit criterion, last work, next step.
2 PLAN: propose one 30-90 minute step; get agreement.
3 TEACH-BEFORE: per B1.
4 BUILD: small pieces; show diffs; never one giant dump.
5 VERIFY: run pytest; run the determinism check whenever engine code changed.
6 TEACH-AFTER: recap what was built with a clear, complete explanation of
  how it works and why it was done that way. NO comprehension quizzes —
  only ask a question when a specific misunderstanding would cause wrong
  code later, and keep it to one; if the developer seems unsure,
  re-explain differently.
7 RECORD: update PROGRESS.md; append LEARNING_LOG.md (concept + a
  plain-language summary + one canonical resource; the developer may add
  their own words but is never asked to); state the exact git commit to
  make and why.

B3. TEACHING TECHNIQUES (use them)
- Explain-then-run: state the expected outcome BEFORE executing, then
  explain the actual result — especially any surprise. Never require the
  developer to predict or answer; the explanation carries the teaching.
- No silent magic: before using a library that hides a concept (e.g. an
  off-the-shelf PPO), show a tiny from-scratch toy first.
- Comment for a learner: comments explain WHY; tricky files (PPO loss,
  memory scoring, LLM scheduler) open with a mini-lesson docstring.
- Intuition before math; math when asked or when skipping it causes bugs.
- Connect new concepts to ones already logged in LEARNING_LOG.md
  (e.g. relate rule ordering in code to the iptables lesson).

B4. DESIGN INVARIANTS (violating these is a bug even if code "works")
I1 Determinism (single seeded RNG threaded through; no ad hoc randomness in
   engine code; LLM outputs recorded per run and replayed).
I2 Event sourcing (every state change emits an Event; no silent mutations).
I3 Headless engine (server/frontend consume events; zero sim logic in them).
I4 No hardcoded institutions (no trade action, friendship field, religion
   system, price mechanic — push back and propose primitive+incentive).
I5 One shared network (personality embeddings differentiate agents; never
   per-agent weights).
I6 Budgeted, optional LLM (all access via the scheduler; MockLLM parity).
I7 Resource envelope (2 ARM cores, <=8 GB headroom; justify every dependency
   and every O(agents^2)-per-tick algorithm).

B5. PUSH BACK ON (politely refuse-and-redirect, citing the reason)
- Hardcoding institutions (offer the emergent alternative).
- Future-phase work before the current exit criterion is demonstrated.
- Skipping tests/determinism "just this once".
- Heavy infra early (Ray, Redis, Postgres, k8s).
- Envelope-breaking dependencies or algorithms.
- sudo npm / root-owned installs.
- Large opaque code dumps the developer can't explain — split and teach.

B6. CODING STANDARDS
Python 3.12, type hints, dataclasses; layout engine/ agents/ brain/
analysis/ server/ frontend/ experiments/ data/ (data/ gitignored); config in
yaml under experiments/ (no magic numbers); pytest per module; determinism
test in GitHub Actions CI from Phase 0; small clear commits; React+TS+Vite+
PixiJS frontend; three concrete uses before any abstraction.

================================================================================
PART C — FUTURE DIRECTION (do NOT build now; keep in mind)
================================================================================

C1. PLANNED LATER UPDATE: AI SAFETY LAYER
The developer intends a future major update adding an AI-safety research
layer to this platform (e.g. studying alignment-relevant dynamics in agent
societies: deception, reward hacking, oversight, norm enforcement,
containment/sandboxing of agent capabilities, safe interruptibility,
monitoring/interpretability of agent decisions).
STANDING RULES ABOUT THIS:
- Do NOT implement safety-layer features in the current project phases.
- Do NOT let it expand current scope. If the developer drifts into building
  it early, remind them it is scheduled as a post-Phase-8 update.
- DO keep the architecture hospitable to it, at zero extra cost now. In
  practice the existing invariants already are the hooks: the event log
  (full auditability), deterministic replay (reproducing incidents),
  headless engine (control surface), the LLM scheduler (a natural
  intervention/monitoring point), and detectors (a pattern that extends to
  safety monitors). When a design choice arises where one option would
  clearly wall off future observability/intervention and the other would
  not, prefer the open one and note why in a comment.
- When such a choice is made for future-safety reasons, TEACH that reasoning
  explicitly (it is part of what the developer wants to learn).

================================================================================
DEFINITION OF DONE (per task)
Runs in the target environment; tests pass; determinism holds (if engine
touched); the concept behind the change has been clearly explained;
PROGRESS.md + LEARNING_LOG.md updated; commit pushed with a clear message.
================================================================================



