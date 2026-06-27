"""Command-line interface for the BHSM prediction registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from .artifact_adapters import artifact_prediction_values, compute_artifact
from .artifact_report import artifact_report_to_markdown, build_artifact_prediction_report
from .artifact_sources import discover_bhsm_artifacts
from .formula_registry import default_formula_registry
from .predictions import PredictionStatus, default_prediction_registry
from .report import build_prediction_report
from .gallery import build_prediction_gallery, gallery_to_markdown
from .live_pdg import is_live_pdg_available, load_reference_with_live_then_fallback
from .notebook_pack import check_notebook_pack, notebook_pack_manifest
from .plotting import generate_gallery_plots, is_matplotlib_available
from .speculative import build_speculative_report, default_speculative_registry
from .theorem_blockers import attempt_theorem_closure, default_theorem_blockers


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

    gallery = commands.add_parser("gallery", help="Build the claim-safe prediction gallery")
    gallery.add_argument("--format", choices=("json", "markdown"), default="json")
    gallery.add_argument("--write", default=None)
    gallery.add_argument("--include-speculative", action="store_true")

    plots = commands.add_parser("plot-gallery", help="Generate deterministic registry/status plots")
    plots.add_argument("--dry-run", action="store_true")
    plots.add_argument("--output-dir", default="artifacts/plots")

    notebooks = commands.add_parser("notebook-pack", help="Inspect the parse-only notebook pack")
    notebooks.add_argument("--manifest", action="store_true")
    notebooks.add_argument("--check", action="store_true")

    commands.add_parser("pdg-status", help="Report optional live PDG adapter availability")
    pdg_fetch = commands.add_parser("pdg-fetch", help="Fetch a comparison reference with fallback")
    pdg_fetch.add_argument("--particle", required=True)
    pdg_fetch.add_argument("--offline-ok", action="store_true")

    speculative = commands.add_parser("speculative", help="Inspect disabled speculative templates")
    spec_commands = speculative.add_subparsers(dest="speculative_command", required=True)
    spec_commands.add_parser("list")
    spec_report = spec_commands.add_parser("report")
    spec_report.add_argument("--format", choices=("json", "text"), default="text")
    spec_report.add_argument("--include-template", action="store_true")

    commands.add_parser("theorem-blockers", help="List exact unresolved theorem objects")
    attempt = commands.add_parser("theorem-attempt", help="Run an artifact-backed closure attempt")
    attempt.add_argument("--blocker", required=True, choices=("X_ch", "neutrino_basis_scale", "neutrino_basis_scale_dirac_majorana", "cp_o_int"))
    attempt.add_argument("--format", choices=("json", "text"), default="text")

    artifact_sources = commands.add_parser("artifact-sources", help="Discover local BHSM artifacts")
    artifact_sources.add_argument("--format", choices=("text", "json"), default="text")

    formula_registry = commands.add_parser("formula-registry", help="List artifact and interface formula callables")
    formula_registry.add_argument("--format", choices=("text", "json"), default="text")

    compute = commands.add_parser("compute-artifact", help="Load one registered local BHSM artifact")
    compute.add_argument("artifact_key", choices=("CKM_matrix_BHSM", "PMNS_matrix_BHSM", "cp_holonomy_phase_attachment", "boundary_constants", "mass_ratios"))
    compute.add_argument("--format", choices=("text", "json"), default="json")

    artifact_predictions = commands.add_parser("artifact-predictions", help="List artifact-backed prediction values")
    artifact_predictions.add_argument("--format", choices=("json",), default="json")

    artifact_report = commands.add_parser("artifact-report", help="Build the provenance-aware artifact report")
    artifact_report.add_argument("--anchor", default="W_boson")
    artifact_report.add_argument("--format", choices=("json", "markdown"), default="json")
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
    if args.command == "gallery":
        gallery = build_prediction_gallery(include_speculative=args.include_speculative)
        output = gallery_to_markdown(gallery) if args.format == "markdown" else json.dumps(gallery.to_dict(), indent=2, sort_keys=True)
        if args.write:
            Path(args.write).write_text(output, encoding="utf-8")
        print(output, end="" if output.endswith("\n") else "\n")
        return 0
    if args.command == "plot-gallery":
        print(json.dumps(generate_gallery_plots(args.output_dir, dry_run=args.dry_run), indent=2, sort_keys=True))
        return 0
    if args.command == "notebook-pack":
        payload = check_notebook_pack() if args.check else notebook_pack_manifest()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if not args.check or payload["passed"] else 1
    if args.command == "pdg-status":
        print(json.dumps({"live_pdg_available": is_live_pdg_available(), "fallback_available": True, "internet_required": False, "reference_only": True}, indent=2, sort_keys=True))
        return 0
    if args.command == "pdg-fetch":
        try:
            payload = load_reference_with_live_then_fallback(args.particle, offline_ok=args.offline_ok).to_dict()
        except (KeyError, RuntimeError) as exc:
            print(json.dumps({"particle_key": args.particle, "status": "unavailable", "error": str(exc)}, indent=2, sort_keys=True))
            return 2
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.command == "speculative":
        if args.speculative_command == "list":
            payload = default_speculative_registry().to_dict()
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _emit(build_speculative_report(args.include_template).to_dict(), args.format)
        return 0
    if args.command == "theorem-blockers":
        print(json.dumps(default_theorem_blockers().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "theorem-attempt":
        key = "neutrino_basis_scale_dirac_majorana" if args.blocker == "neutrino_basis_scale" else args.blocker
        _emit(attempt_theorem_closure(key).to_dict(), args.format)
        return 0
    if args.command == "artifact-sources":
        payload = discover_bhsm_artifacts().to_dict()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"{payload['index_name']} ({payload['artifact_count']} local sources)")
            for source in payload["sources"]:
                print(f"{source['source_status']} | {source['path']} | {source['detected_schema']}")
        return 0
    if args.command == "formula-registry":
        payload = default_formula_registry().to_dict()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(payload["registry_name"])
            for row in payload["formula_entries"]:
                print(f"{row['formula_key']} | {row['status']} | {row['claim_boundary']}")
        return 0
    if args.command == "compute-artifact":
        payload = compute_artifact(args.artifact_key).to_dict()
        _emit(payload, args.format)
        return 0
    if args.command == "artifact-predictions":
        print(json.dumps(artifact_prediction_values(), indent=2, sort_keys=True))
        return 0
    if args.command == "artifact-report":
        artifact_report = build_artifact_prediction_report(args.anchor)
        if args.format == "markdown":
            print(artifact_report_to_markdown(artifact_report), end="")
        else:
            print(json.dumps(artifact_report.to_dict(), indent=2, sort_keys=True))
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
