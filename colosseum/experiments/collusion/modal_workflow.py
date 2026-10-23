"""Guard-railed CLI for the Modal-backed collusion workflow."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from experiments.collusion.modal_config import check_endpoint, load_prepared_config, validate_modal_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "endpoint-check", "run", "compare"):
        item = sub.add_parser(name)
        item.add_argument("--config", required=True)
        if name in {"run", "compare"}:
            item.add_argument("--allow-inference", action="store_true", help="Required acknowledgement before a paid remote run.")
            item.add_argument("--out-dir")
            item.add_argument("--dry-run", action="store_true", help="Validate and print the plan without an endpoint request or inference.")
    locate = sub.add_parser("locate")
    locate.add_argument("--root", required=True)
    args = parser.parse_args()

    if args.command == "locate":
        root = Path(args.root)
        for path in sorted(root.rglob("run_config.json")):
            print(path.parent)
        return

    cfg = load_prepared_config(args.config)
    validate_modal_config(cfg)
    if args.command == "validate":
        print("Configuration is valid; no endpoint call was made.")
        return
    if args.command == "endpoint-check":
        print(json.dumps({"models": check_endpoint(cfg)}, indent=2))
        return
    if args.dry_run:
        experiment = cfg.get("experiment") or {}
        print(json.dumps({
            "dry_run": True,
            "experiment_id": experiment.get("experiment_id"),
            "seeds": experiment.get("seeds"),
            "sweeps": experiment.get("sweeps"),
        }, indent=2))
        return
    if not args.allow_inference:
        parser.error("Refusing remote inference without --allow-inference.")

    # The runner reloads and redacts the same config, and additionally records a
    # manifest/config snapshot beside raw traces.
    from experiments.collusion.run import run_from_config
    output = asyncio.run(run_from_config(args.config, out_dir=args.out_dir))
    print(f"Wrote results to: {output}")


if __name__ == "__main__":
    main()
