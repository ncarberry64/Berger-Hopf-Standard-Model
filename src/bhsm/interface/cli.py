"""Command-line interface for the BHSM prediction registry."""

from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from .predictions import PredictionStatus, default_prediction_registry
from .report import build_prediction_report


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if "entries" in payload:
        for entry in payload["entries"]:
            print(f"{entry['particle_key']} | {entry['display_name']} | {entry['default_status']}")
            print(f"  {entry['claim_boundary']}")
        return
    if "report_name" in payload:
        print(f"{payload['report_name']} ({payload['release_basis']})")
        print(f"calibration_anchor: {payload['anchor_particle']}")
        for row in payload["registry_statuses"]:
            print(f"{row['particle_key']}: {row['status']}")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m bhsm.interface", description="Offline BHSM prediction registry and reviewer report CLI")
    commands = parser.add_subparsers(dest="command", required=True)

    registry = commands.add_parser("registry", help="List prediction registry entries")
    registry.add_argument("--format", choices=("text", "json"), default="text")

    status = commands.add_parser("status", help="Show one registry entry")
    status.add_argument("particle_key")
    status.add_argument("--format", choices=("text", "json"), default="text")

    predict = commands.add_parser("predict", help="Run a deterministic interface demonstration")
    predict.add_argument("--particle", required=True)
    predict.add_argument("--anchor", default=None)
    predict.add_argument("--mode", choices=("calibration", "prediction", "demo"), default="demo")
    predict.add_argument("--format", choices=("text", "json"), default="json")

    report = commands.add_parser("report", help="Build a combined reviewer report")
    report.add_argument("--anchor", default="W_boson")
    report.add_argument("--particles", default="W_boson,electron_neutrino")
    report.add_argument("--include-open-theorem", action="store_true")
    report.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = default_prediction_registry()
    if args.command == "registry":
        _emit(registry.to_dict(), args.format)
        return 0
    if args.command == "status":
        entry = registry.get(args.particle_key)
        if entry is None:
            _emit({"particle_key": args.particle_key, "status": PredictionStatus.UNKNOWN_OR_UNREGISTERED.value}, args.format)
            return 2
        _emit(entry.to_dict(), args.format)
        return 0
    if args.command == "predict":
        if args.particle not in ("W_boson", "electron_neutrino"):
            _emit({"particle_key": args.particle, "status": PredictionStatus.UNKNOWN_OR_UNREGISTERED.value, "prediction_supported": False}, args.format)
            return 2
        anchor = args.anchor
        if args.particle == "W_boson" and args.mode == "calibration":
            anchor = "W_boson"
        elif args.particle == "electron_neutrino" and anchor is None:
            anchor = "W_boson"
        report = build_prediction_report(anchor_particle=anchor, particles=(args.particle,), registry=registry)
        _emit(report.to_dict(), args.format)
        return 0
    particles = tuple(item.strip() for item in args.particles.split(",") if item.strip())
    report = build_prediction_report(
        anchor_particle=args.anchor,
        particles=particles,
        include_open_theorem_entries=args.include_open_theorem,
        registry=registry,
    )
    _emit(report.to_dict(), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
