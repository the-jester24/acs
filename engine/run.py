"""CLI entry point: run a simulation from a yaml config, write the event log.

Usage:
    python -m engine.run experiments/day1.yaml

Writes data/run_seed<seed>.jsonl — one JSON event per line (JSONL). Line-based
logs diff cleanly and can be streamed later by the server (Phase-friendly).
"""

import sys
from pathlib import Path

import yaml

from engine.engine import Engine


def main() -> None:
    config_path = Path(sys.argv[1])
    config = yaml.safe_load(config_path.read_text())

    engine = Engine(
        seed=config["seed"],
        num_agents=config["num_agents"],
        grid_size=config["grid_size"],
    )
    events = engine.run(config["ticks"])

    out = Path("data") / f"run_seed{config['seed']}.jsonl"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(e.to_json() for e in events) + "\n")
    print(f"{len(events)} events -> {out}")


if __name__ == "__main__":
    main()
