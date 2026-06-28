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
from .theorem_closure import build_cp_o_int_field_action_report, build_cp_o_int_report, build_theorem_closure_report, evaluate_theorem
from .theorem_closure.closure_report import theorem_closure_report_to_markdown
from .theorem_closure.cp_o_int_action import load_cp_o_int_candidate_template
from .theorem_closure.cp_o_int_report import cp_o_int_report_to_markdown
from .theorem_closure.cp_o_int_sprint_c_report import cp_o_int_sprint_c_to_markdown
from .minimal_action import build_minimal_action_report, close_minimal_action, minimal_action_report_to_markdown, minimal_action_status
from .neutrino_propagation import (
    build_neutrino_propagation_report,
    build_numerical_closure,
    neutrino_propagation_report_to_markdown,
)
from .neutrino_propagation.curvature_threshold import build_background_coupling, build_curvature_threshold, threshold_response
from .neutrino_propagation.effective_mass import load_neutral_scale_law
from .neutrino_propagation.neutral_kernel import load_neutral_kernel
from .neutrino_propagation.observable_map import build_neutrino_observable_map
from .neutrino_propagation.propagation_state import canonical_channel_states
from .neutrino_scale import (
    analyze_neutral_boundary_measure,
    build_legacy_curvature_scale_report,
    build_legacy_neutral_scale_candidate,
    build_neutral_radius_curvature_closure,
    build_neutral_radius_curvature_report,
    build_neutral_scale_candidates,
    build_neutral_scale_report,
    build_threshold_energy_map,
    derive_neutral_scale_law,
    derive_or_locate_neutral_curvature_mapping,
    derive_or_locate_neutrino_propagation_radius,
    index_legacy_curvature_artifacts,
    legacy_curvature_scale_report_to_markdown,
    neutral_radius_curvature_report_to_markdown,
    load_curvature_mass_functional_from_legacy_artifacts,
    compute_dimensionful_neutrino_mass_candidate,
    search_neutral_physical_curvature_map,
    search_neutral_propagation_radius,
    neutral_scale_report_to_markdown,
)
from .neutrino_spectral import (
    audit_legacy_gravitational_mass_formula_dimensions,
    audit_neutral_kernel_positivity,
    build_neutral_spectral_gap_candidate,
    build_neutral_spectral_report,
    load_neutral_mass_gap_action,
    neutral_spectral_report_to_markdown,
    search_neutral_stiffness_ratio,
    audit_neutral_kernel_exact,
    build_neutral_positivity_report,
    build_projected_neutral_kernel,
    derive_or_load_neutral_admissible_domain,
    neutral_positivity_report_to_markdown,
    prove_neutral_positivity_on_domain,
    search_admissible_positivity_counterexample,
)
from .neutrino_action import (
    build_neutral_action_closure_report,
    build_neutral_action_spectral_closure,
    derive_neutral_stiffness_length,
    derive_or_locate_physical_neutral_curvature_map,
    derive_response_cone_from_neutral_action,
    neutral_action_closure_report_to_markdown,
    search_neutral_action_sources,
)
from .neutrino_closure_status import (
    build_v1_5_status_stabilization_report,
    neutrino_closure_status_to_markdown,
)
from .full_completion import (
    build_boundary_measure_closure,
    build_full_completion_blocker_ledger,
    build_full_completion_priority_map,
    build_full_completion_status_report,
    full_completion_status_to_markdown,
    select_highest_leverage_target,
)


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

    closure_report = commands.add_parser("theorem-closure-report", help="Run all strict theorem proof-gate attempts")
    closure_report.add_argument("--format", choices=("json", "markdown"), default="json")

    close_theorem = commands.add_parser("close-theorem", help="Attempt one theorem closure without inferring missing objects")
    close_theorem.add_argument("theorem_key", choices=("X_ch", "neutrino_basis_scale", "cp_o_int"))
    close_theorem.add_argument("--format", choices=("json", "text"), default="json")

    proof_gates = commands.add_parser("theorem-proof-gates", help="Show proof gates for one theorem attempt")
    proof_gates.add_argument("theorem_key", choices=("X_ch", "neutrino_basis_scale", "cp_o_int"))
    proof_gates.add_argument("--format", choices=("json", "text"), default="json")

    cp_report = commands.add_parser("cp-o-int-report", help="Run the focused standalone CP O_int attachment audit")
    cp_report.add_argument("--format", choices=("json", "markdown"), default="json")

    cp_stages = commands.add_parser("cp-o-int-stages", help="Show staged CP O_int evaluation")
    cp_stages.add_argument("--format", choices=("json",), default="json")

    cp_gates = commands.add_parser("cp-o-int-proof-gates", help="Show focused CP O_int proof gates")
    cp_gates.add_argument("--format", choices=("json",), default="json")

    cp_candidate = commands.add_parser("cp-o-int-candidate", help="Inspect the disabled CP O_int author template")
    cp_candidate.add_argument("--format", choices=("json",), default="json")

    cp_field_action = commands.add_parser("cp-o-int-field-action", help="Build the source-traced symbolic CP O_int field/action candidate")
    cp_field_action.add_argument("--format", choices=("json", "markdown"), default="json")

    cp_field_stages = commands.add_parser("cp-o-int-field-action-stages", help="Show Sprint C construction stages")
    cp_field_stages.add_argument("--format", choices=("json",), default="json")

    cp_production = commands.add_parser("cp-o-int-production-eligibility", help="Show production and runtime eligibility")
    cp_production.add_argument("--format", choices=("json",), default="json")

    cp_action = commands.add_parser("cp-o-int-action-candidate", help="Show the symbolic action-density candidate")
    cp_action.add_argument("--format", choices=("json",), default="json")

    minimal = commands.add_parser("minimal-action", help="Build the minimal action-closure report")
    minimal.add_argument("--format", choices=("json",), default="json")
    minimal_report = commands.add_parser("minimal-action-report", help="Render the minimal action-closure report")
    minimal_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    close_minimal = commands.add_parser("close-minimal-action", help="Evaluate one minimal-action theorem")
    close_minimal.add_argument("theorem_key", choices=("cp_o_int", "X_ch", "neutrino_basis_scale"))
    close_minimal.add_argument("--format", choices=("json",), default="json")
    commands.add_parser("minimal-action-status", help="Show concise minimal-action theorem statuses")
    neutrino = commands.add_parser("neutrino-propagation", help="Build the conditional neutrino propagation-mass candidate")
    neutrino.add_argument("--format", choices=("json",), default="json")
    neutrino_report = commands.add_parser("neutrino-propagation-report", help="Render the neutrino propagation-mass report")
    neutrino_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    neutrino_mass = commands.add_parser("neutrino-effective-mass", help="Show dimensionless neutrino propagation-mass channel responses")
    neutrino_mass.add_argument("--format", choices=("json",), default="json")
    neutrino_map = commands.add_parser("neutrino-observable-map", help="Show the neutrino observable and comparison policy")
    neutrino_map.add_argument("--format", choices=("json",), default="json")
    neutrino_scale = commands.add_parser("neutrino-scale-law", help="Show the audited neutral scale law and dimensional blocker")
    neutrino_scale.add_argument("--format", choices=("json",), default="json")
    neutrino_threshold = commands.add_parser("neutrino-threshold-response", help="Show artifact-backed threshold response rows")
    neutrino_threshold.add_argument("--format", choices=("json",), default="json")
    scale_candidates = commands.add_parser("neutral-scale-candidates", help="Classify local neutral scale candidates")
    scale_candidates.add_argument("--format", choices=("json",), default="json")
    threshold_map = commands.add_parser("neutral-threshold-energy-map", help="Audit the neutral threshold-to-energy map")
    threshold_map.add_argument("--format", choices=("json",), default="json")
    boundary_measure = commands.add_parser("neutral-boundary-measure", help="Audit the neutral boundary measure")
    boundary_measure.add_argument("--format", choices=("json",), default="json")
    dimensionful_mass = commands.add_parser("neutrino-dimensionful-mass", help="Attempt a unit-safe neutrino mass output")
    dimensionful_mass.add_argument("--format", choices=("json",), default="json")
    scale_report = commands.add_parser("neutrino-scale-report", help="Render the neutral scale closure report")
    scale_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    legacy_artifacts = commands.add_parser("legacy-curvature-artifacts", help="Index bundled legacy curvature-threshold theory artifacts")
    legacy_artifacts.add_argument("--format", choices=("json",), default="json")
    legacy_functional = commands.add_parser("curvature-mass-functional", help="Show the legacy curvature mass functional with provenance")
    legacy_functional.add_argument("--format", choices=("json",), default="json")
    propagation_radius = commands.add_parser("neutrino-propagation-radius", help="Search for a physical neutral propagation radius")
    propagation_radius.add_argument("--format", choices=("json",), default="json")
    curvature_mapping = commands.add_parser("neutral-curvature-mapping", help="Audit the neutral response-to-curvature map")
    curvature_mapping.add_argument("--format", choices=("json",), default="json")
    legacy_scale = commands.add_parser("legacy-neutral-scale", help="Build the legacy curvature neutral-scale candidate")
    legacy_scale.add_argument("--format", choices=("json",), default="json")
    legacy_report = commands.add_parser("legacy-neutral-scale-report", help="Render the legacy curvature neutral-scale audit")
    legacy_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    radius_search = commands.add_parser("neutral-propagation-radius", help="Search for a neutral propagation radius without empirical calibration")
    radius_search.add_argument("--format", choices=("json",), default="json")
    physical_curvature = commands.add_parser("neutral-physical-curvature", help="Search for a physical neutral-curvature map")
    physical_curvature.add_argument("--format", choices=("json",), default="json")
    radius_curvature = commands.add_parser("neutral-radius-curvature-closure", help="Build the coupled radius/curvature closure")
    radius_curvature.add_argument("--format", choices=("json",), default="json")
    dimensionful_candidate = commands.add_parser("dimensionful-neutrino-mass-candidate", help="Build the dimensionally guarded neutral mass candidate")
    dimensionful_candidate.add_argument("--format", choices=("json",), default="json")
    radius_curvature_report = commands.add_parser("neutral-radius-curvature-report", help="Render the radius/curvature closure report")
    radius_curvature_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    mass_gap_action = commands.add_parser("neutrino-mass-gap-action", help="Load the scalar mass-gap analogue and conditional neutral action")
    mass_gap_action.add_argument("--format", choices=("json",), default="json")
    dimensional_gate = commands.add_parser("legacy-dimensional-gate", help="Audit the legacy gravitational expression dimensions")
    dimensional_gate.add_argument("--format", choices=("json",), default="json")
    stiffness_ratio = commands.add_parser("neutral-stiffness-ratio", help="Search for the neutral action stiffness ratio")
    stiffness_ratio.add_argument("--format", choices=("json",), default="json")
    spectral_gap = commands.add_parser("neutral-spectral-gap", help="Build the conditional neutral spectral-gap candidate")
    spectral_gap.add_argument("--format", choices=("json",), default="json")
    kernel_positivity = commands.add_parser("neutral-kernel-positivity", help="Audit raw and admissible neutral-kernel positivity")
    kernel_positivity.add_argument("--format", choices=("json",), default="json")
    spectral_report = commands.add_parser("neutral-spectral-report", help="Render the neutral spectral-stiffness report")
    spectral_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    exact_kernel = commands.add_parser("neutral-kernel-exact-audit", help="Audit the exact rational neutral kernel")
    exact_kernel.add_argument("--format", choices=("json",), default="json")
    admissible_domain = commands.add_parser("neutral-admissible-domain", help="Load the measurement-supported response cone")
    admissible_domain.add_argument("--format", choices=("json",), default="json")
    positivity_proof = commands.add_parser("neutral-positivity-proof", help="Prove copositivity on the admissible response cone")
    positivity_proof.add_argument("--format", choices=("json",), default="json")
    positivity_counterexample = commands.add_parser("neutral-positivity-counterexample", help="Search the admissible cone for a negative quadratic value")
    positivity_counterexample.add_argument("--format", choices=("json",), default="json")
    positivity_report = commands.add_parser("neutral-positivity-report", help="Render the admissible neutral positivity report")
    positivity_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    action_search = commands.add_parser("neutral-action-source-search", help="Inventory neutral action sources and normalization gaps")
    action_search.add_argument("--format", choices=("json",), default="json")
    action_stiffness = commands.add_parser("neutral-action-stiffness", help="Extract neutral kinetic and curvature stiffness")
    action_stiffness.add_argument("--format", choices=("json",), default="json")
    action_curvature = commands.add_parser("neutral-physical-curvature-map", help="Audit the physical neutral curvature unit map")
    action_curvature.add_argument("--format", choices=("json",), default="json")
    action_cone = commands.add_parser("neutral-action-response-cone", help="Audit action support for the neutral response cone")
    action_cone.add_argument("--format", choices=("json",), default="json")
    action_closure = commands.add_parser("neutral-action-spectral-closure", help="Build the neutral action spectral closure")
    action_closure.add_argument("--format", choices=("json",), default="json")
    action_report = commands.add_parser("neutral-action-closure-report", help="Render the neutral action closure report")
    action_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    closure_status = commands.add_parser("neutrino-closure-status", help="Show the canonical neutral closure status split")
    closure_status.add_argument("--format", choices=("markdown", "json"), default="json")
    completion_ledger = commands.add_parser("full-completion-ledger", help="Show the sixteen-category BHSM completion blocker ledger")
    completion_ledger.add_argument("--format", choices=("json",), default="json")
    completion_priority = commands.add_parser("full-completion-priority-map", help="Show predeclared completion-target scores")
    completion_priority.add_argument("--format", choices=("json",), default="json")
    completion_status = commands.add_parser("full-completion-status", help="Render the conservative BHSM full-completion status")
    completion_status.add_argument("--format", choices=("markdown", "json"), default="markdown")
    completion_target = commands.add_parser("full-completion-selected-target", help="Show the selected closure target and result")
    completion_target.add_argument("--format", choices=("json",), default="json")
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
    if args.command == "theorem-closure-report":
        closure_report = build_theorem_closure_report()
        if args.format == "markdown":
            print(theorem_closure_report_to_markdown(closure_report), end="")
        else:
            print(json.dumps(closure_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "close-theorem":
        result = evaluate_theorem(args.theorem_key)
        _emit(result.to_dict(), args.format)
        return 0
    if args.command == "theorem-proof-gates":
        result = evaluate_theorem(args.theorem_key)
        payload = {
            "theorem_key": result.theorem_key,
            "closure_status": result.closure_status,
            "promotion_allowed": result.promotion_allowed,
            "proof_gates": [gate.__dict__ for gate in result.proof_gates],
        }
        _emit(payload, args.format)
        return 0
    if args.command == "cp-o-int-report":
        cp_report = build_cp_o_int_report()
        if args.format == "markdown":
            print(cp_o_int_report_to_markdown(cp_report), end="")
        else:
            print(json.dumps(cp_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "cp-o-int-stages":
        cp_report = build_cp_o_int_report()
        print(json.dumps({"theorem_key": cp_report.theorem_key, "status": cp_report.status_after, "deepest_valid_stage": cp_report.deepest_valid_stage, "stages": [stage.__dict__ for stage in cp_report.stages]}, indent=2, sort_keys=True))
        return 0
    if args.command == "cp-o-int-proof-gates":
        cp_report = build_cp_o_int_report()
        print(json.dumps({"theorem_key": cp_report.theorem_key, "status": cp_report.status_after, "promotion_allowed": cp_report.promotion_allowed, "proof_gates": [gate.__dict__ for gate in cp_report.proof_gates]}, indent=2, sort_keys=True))
        return 0
    if args.command == "cp-o-int-candidate":
        template = load_cp_o_int_candidate_template()
        cp_report = build_cp_o_int_report()
        print(json.dumps({"template": template, "evaluation": {"status": cp_report.status_after, "promoted": cp_report.promoted, "conditional_author_axiom_used": cp_report.conditional_author_axiom_used}}, indent=2, sort_keys=True))
        return 0
    if args.command == "cp-o-int-field-action":
        cp_report = build_cp_o_int_field_action_report()
        if args.format == "markdown":
            print(cp_o_int_sprint_c_to_markdown(cp_report), end="")
        else:
            print(json.dumps(cp_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "cp-o-int-field-action-stages":
        cp_report = build_cp_o_int_field_action_report()
        print(json.dumps({"candidate_key": cp_report.candidate_key, "status": cp_report.status_after, "deepest_valid_stage_before": cp_report.deepest_valid_stage_before, "deepest_valid_stage_after": cp_report.deepest_valid_stage_after, "first_failed_required_stage": cp_report.first_failed_required_stage, "stages": [stage.__dict__ for stage in cp_report.stages]}, indent=2, sort_keys=True))
        return 0
    if args.command == "cp-o-int-production-eligibility":
        cp_report = build_cp_o_int_field_action_report()
        print(json.dumps({"candidate_key": cp_report.candidate_key, "production_eligible": cp_report.production_eligible, "runtime_export_eligible": cp_report.runtime_export_eligible, "production_eligibility": cp_report.production_eligibility, "runtime_gates_changed": cp_report.runtime_gate_changes}, indent=2, sort_keys=True))
        return 0
    if args.command == "cp-o-int-action-candidate":
        cp_report = build_cp_o_int_field_action_report()
        print(json.dumps({"candidate_key": cp_report.candidate_key, "candidate_status": cp_report.candidate_status, "theorem_status": cp_report.status_after, "action_density": cp_report.action_density, "symbolic_callable": cp_report.symbolic_callable, "production_eligible": cp_report.production_eligible}, indent=2, sort_keys=True))
        return 0
    if args.command == "minimal-action":
        print(json.dumps(build_minimal_action_report().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "minimal-action-report":
        minimal_report = build_minimal_action_report()
        if args.format == "markdown":
            print(minimal_action_report_to_markdown(minimal_report), end="")
        else:
            print(json.dumps(minimal_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "close-minimal-action":
        print(json.dumps(close_minimal_action(args.theorem_key).to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "minimal-action-status":
        print(json.dumps(minimal_action_status(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-propagation":
        print(json.dumps(build_neutrino_propagation_report().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-propagation-report":
        neutrino_report = build_neutrino_propagation_report()
        if args.format == "markdown":
            print(neutrino_propagation_report_to_markdown(neutrino_report), end="")
        else:
            print(json.dumps(neutrino_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-effective-mass":
        report = build_numerical_closure()
        print(json.dumps({"status": report.closure.status_after, "formula": report.closure.effective_mass_formula, "channel_results": [row.to_dict() for row in report.channel_results]}, indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-observable-map":
        print(json.dumps(build_neutrino_observable_map().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-scale-law":
        print(json.dumps(derive_neutral_scale_law().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-threshold-response":
        kernel = load_neutral_kernel()
        threshold = build_curvature_threshold(kernel)
        background = build_background_coupling(kernel)
        rows = []
        for state in canonical_channel_states(len(kernel.matrix)):
            response_norm, coupled, excess = threshold_response(kernel, state, threshold, background)
            rows.append({"state": state.label, "kernel_response_norm": response_norm, "coupled_response": coupled, "threshold_excess": excess})
        print(json.dumps({"threshold": threshold.to_dict(), "background_coupling": background.to_dict(), "rows": rows}, indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-scale-candidates":
        print(json.dumps({"candidates": [row.to_dict() for row in build_neutral_scale_candidates()]}, indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-threshold-energy-map":
        print(json.dumps(build_threshold_energy_map().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-boundary-measure":
        print(json.dumps(analyze_neutral_boundary_measure().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-dimensionful-mass":
        scale_report = build_neutral_scale_report()
        legacy_scale_report = build_legacy_curvature_scale_report()
        radius_curvature_closure = build_neutral_radius_curvature_closure()
        print(json.dumps({
            "status": scale_report.scale_result.status_after,
            "dimensionful_mass_output_produced": scale_report.dimensionful_mass_output_produced,
            "legacy_curvature_mass_functional_available": legacy_scale_report.result.mass_functional_available,
            "propagation_radius_available": legacy_scale_report.result.propagation_radius_available,
            "neutral_curvature_mapping_available": legacy_scale_report.result.neutral_curvature_mapping_available,
            "physical_curvature_units_available": legacy_scale_report.neutral_curvature_mapping.physical_curvature_units_available,
            "dimensionful_mass_possible": legacy_scale_report.result.dimensionful_mass_possible,
            "symbolic_propagation_radius_candidate": radius_curvature_closure.radius.symbolic_candidate_found,
            "symbolic_physical_curvature_candidate": radius_curvature_closure.curvature_map.symbolic_candidate_found,
            "mass_dimension_consistency_passed": radius_curvature_closure.dimensional_consistency_passed,
            "v1_2_status": radius_curvature_closure.status,
            "channel_results": [row.to_dict() for row in scale_report.dimensionful_mass_attempt],
        }, indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-scale-report":
        scale_report = build_neutral_scale_report()
        if args.format == "markdown":
            print(neutral_scale_report_to_markdown(scale_report), end="")
        else:
            print(json.dumps(scale_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "legacy-curvature-artifacts":
        print(json.dumps({"artifacts": [row.to_dict() for row in index_legacy_curvature_artifacts()]}, indent=2, sort_keys=True))
        return 0
    if args.command == "curvature-mass-functional":
        print(json.dumps(load_curvature_mass_functional_from_legacy_artifacts().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-propagation-radius":
        print(json.dumps(derive_or_locate_neutrino_propagation_radius().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-curvature-mapping":
        print(json.dumps(derive_or_locate_neutral_curvature_mapping().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "legacy-neutral-scale":
        print(json.dumps(build_legacy_neutral_scale_candidate().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "legacy-neutral-scale-report":
        legacy_report = build_legacy_curvature_scale_report()
        if args.format == "markdown":
            print(legacy_curvature_scale_report_to_markdown(legacy_report), end="")
        else:
            print(json.dumps(legacy_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-propagation-radius":
        print(json.dumps(search_neutral_propagation_radius().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-physical-curvature":
        print(json.dumps(search_neutral_physical_curvature_map().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-radius-curvature-closure":
        print(json.dumps(build_neutral_radius_curvature_closure().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "dimensionful-neutrino-mass-candidate":
        closure = build_neutral_radius_curvature_closure()
        print(json.dumps(compute_dimensionful_neutrino_mass_candidate(closure).to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-radius-curvature-report":
        report = build_neutral_radius_curvature_report()
        if args.format == "markdown":
            print(neutral_radius_curvature_report_to_markdown(report), end="")
        else:
            print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-mass-gap-action":
        print(json.dumps(load_neutral_mass_gap_action().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "legacy-dimensional-gate":
        print(json.dumps(audit_legacy_gravitational_mass_formula_dimensions().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-stiffness-ratio":
        print(json.dumps(search_neutral_stiffness_ratio().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-spectral-gap":
        print(json.dumps(build_neutral_spectral_gap_candidate().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-kernel-positivity":
        print(json.dumps(audit_neutral_kernel_positivity().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-spectral-report":
        spectral_report = build_neutral_spectral_report()
        if args.format == "markdown":
            print(neutral_spectral_report_to_markdown(spectral_report), end="")
        else:
            print(json.dumps(spectral_report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-kernel-exact-audit":
        print(json.dumps(audit_neutral_kernel_exact().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-admissible-domain":
        print(json.dumps(derive_or_load_neutral_admissible_domain().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-positivity-proof":
        print(json.dumps(prove_neutral_positivity_on_domain().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-positivity-counterexample":
        print(json.dumps(search_admissible_positivity_counterexample().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-positivity-report":
        report = build_neutral_positivity_report()
        if args.format == "markdown":
            print(neutral_positivity_report_to_markdown(report), end="")
        else:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-action-source-search":
        print(json.dumps(search_neutral_action_sources().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-action-stiffness":
        print(json.dumps(derive_neutral_stiffness_length().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-physical-curvature-map":
        print(json.dumps(derive_or_locate_physical_neutral_curvature_map().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-action-response-cone":
        print(json.dumps(derive_response_cone_from_neutral_action().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-action-spectral-closure":
        print(json.dumps(build_neutral_action_spectral_closure().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutral-action-closure-report":
        report = build_neutral_action_closure_report()
        if args.format == "markdown":
            print(neutral_action_closure_report_to_markdown(report), end="")
        else:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "neutrino-closure-status":
        report = build_v1_5_status_stabilization_report()
        if args.format == "markdown":
            print(neutrino_closure_status_to_markdown(report), end="")
        else:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "full-completion-ledger":
        blockers = build_full_completion_blocker_ledger()
        print(json.dumps({"blocker_count": len(blockers), "blockers": [row.to_dict() for row in blockers]}, indent=2, sort_keys=True))
        return 0
    if args.command == "full-completion-priority-map":
        rows = build_full_completion_priority_map()
        print(json.dumps({"selected_target": rows[0].target_id, "rows": [row.to_dict() for row in rows]}, indent=2, sort_keys=True))
        return 0
    if args.command == "full-completion-status":
        report = build_full_completion_status_report()
        if args.format == "markdown":
            print(full_completion_status_to_markdown(report), end="")
        else:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "full-completion-selected-target":
        selected = select_highest_leverage_target()
        closure = build_boundary_measure_closure()
        print(json.dumps({"selected_target": selected.to_dict(), "closure_attempt": closure.to_dict()}, indent=2, sort_keys=True))
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
