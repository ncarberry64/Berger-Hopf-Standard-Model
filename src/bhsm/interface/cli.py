"""Command-line interface for the BHSM prediction registry."""

from __future__ import annotations

import argparse
import json
import sys
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
from .neutrino_bedrock import load_neutrino_bedrock_status, neutrino_bedrock_status_to_markdown
from .full_completion import (
    build_boundary_measure_closure,
    build_full_completion_blocker_ledger,
    build_full_completion_priority_map,
    build_full_completion_status_report,
    full_completion_status_to_markdown,
    select_highest_leverage_target,
)
from .charged_closure import (
    audit_charged_closure_dimensions,
    build_charged_closure_report,
    charged_closure_report_to_markdown,
    derive_or_locate_charged_action_stiffness,
    derive_or_locate_charged_mixing_law_source,
    derive_or_locate_ckm_exponent_source,
    derive_or_locate_eta_l_source,
    search_charged_closure_sources,
)
from .common_16 import (
    audit_common_16_bridge_beta,
    audit_common_16_ckm_transport,
    audit_common_16_incidence,
    audit_common_16_provenance,
    build_final_completion_report,
    final_completion_report_to_markdown,
    search_common_16_sources,
)
from .science_hardening import emit_hardening_payload
from .primitive_charged_incidence import (
    audit_bridge_beta_identity,
    audit_ckm_log_transport,
    audit_external_reproduction_status,
    audit_overlap_4_over_3,
    audit_physical_normalization,
    audit_rho_gcd_selection,
    build_primitive_charged_incidence_report,
)
from .action_lemmas import (
    audit_maximal_overlap_bridge_rule,
    audit_primitive_lattice_rule,
    build_action_lemma_closure_report,
    prove_log_transport_averaging,
    search_action_lemma_sources,
)
from .ckm_channel_equivalence import (
    audit_ckm_channel_application,
    audit_ckm_channel_counts,
    audit_maximal_sector_selection,
    build_ckm_channel_equivalence_report,
    search_ckm_channel_sources,
)
from .ckm_bidirectional_channel import (
    audit_bidirectional_channel_count,
    audit_bidirectional_log_transport_application,
    audit_ckm_adjoint_pair_selection,
    audit_ckm_channel_alternative_resolution,
    build_ckm_bidirectional_channel_report,
    search_ckm_bidirectional_sources,
)
from .normalized_action_adjoint_pair import (
    audit_ckm_alternative_channel_blockers,
    audit_ckm_transport_space_gate,
    audit_hermitian_charged_current_action_rule,
    audit_normalized_action_adjoint_pair_selection,
    build_normalized_action_adjoint_pair_report,
    normalized_action_adjoint_pair_report_to_markdown,
    search_normalized_action_adjoint_pair_sources,
)
from .charged_current_action import (
    audit_ckm_transport_space_application_gate,
    audit_charged_current_transport_space,
    audit_hermitian_adjoint_pair_transport_gate,
    audit_normalized_charged_current_action_term,
    build_charged_current_action_report,
    charged_current_action_report_to_markdown,
    search_charged_current_action_sources,
)
from .ckm_bounded_interface_normalization import (
    audit_ckm_bounded_interface_term,
    audit_ckm_identification_gate,
    audit_ckm_transport_space_selection,
    audit_normalized_projector_sandwich,
    audit_paired_term_normalization,
    audit_projector_domain_codomain,
    build_ckm_bounded_interface_report,
    ckm_bounded_interface_report_to_markdown,
    search_ckm_bounded_interface_sources,
)
from .ckm_boundary_measure_normalization import (
    audit_boundary_measure_source,
    audit_coefficient_normalization,
    audit_measure_coefficient_pair,
    audit_normalized_ckm_action_candidate,
    audit_paired_normalization_rule,
    audit_projector_sandwich_requirement,
    audit_transport_space_blocker,
    boundary_measure_normalization_report_to_markdown,
    build_boundary_measure_normalization_report,
    search_boundary_measure_normalization_sources,
)
from .ckm_coefficient_form_source import (
    search_coefficient_form_sources, audit_weak_charged_current_form,
    audit_g2_source, audit_alpha2_source, audit_weak_coupling_convention,
    audit_ckm_coefficient_form, audit_ckm_coefficient_value_source,
    audit_measure_coefficient_attachment, build_coefficient_form_report,
    coefficient_form_report_to_markdown,
)
from .weak_gauge_action_source import (
    audit_alpha2_bh_action_source,
    audit_ckm_value_source_blocker,
    audit_g2_bh_action_source,
    audit_normalized_weak_gauge_action_coefficient,
    audit_normalized_weak_gauge_action_skeleton,
    audit_weak_gauge_algebra_source,
    audit_weak_gauge_coupling_convention,
    audit_weak_gauge_trace_normalization,
    build_weak_gauge_action_source_report,
    search_weak_gauge_action_sources,
    weak_gauge_action_source_report_to_markdown,
)
from .gauge_coupling_quantum import (
    audit_alpha_i_action_derivation,
    audit_ckm_value_source_update,
    audit_g2_action_source_update,
    audit_gauge_coupling_action_attachment,
    audit_gauge_coupling_registry_pattern,
    audit_gauge_coupling_volume_denominator,
    audit_gauge_sector_weight_source,
    audit_universal_gauge_coupling_quantum,
    build_gauge_coupling_quantum_report,
    gauge_coupling_quantum_report_to_markdown,
    search_gauge_coupling_quantum_sources,
)
from .full_action_closure import (
    COMMAND_BUILDERS as FULL_ACTION_COMMAND_BUILDERS,
    full_action_closure_report_to_markdown,
)
from .boundary_collar_measure import (
    COMMAND_BUILDERS as BOUNDARY_MEASURE_COMMAND_BUILDERS,
    boundary_collar_measure_report_to_markdown,
)
from .berger_frame_weighting import (
    COMMAND_BUILDERS as BERGER_FRAME_COMMAND_BUILDERS,
    berger_frame_weighting_report_to_markdown,
)
from .gauge_coframe_hodge import COMMAND_BUILDERS as GAUGE_COFRAME_COMMAND_BUILDERS, gauge_coframe_hodge_report_to_markdown
from .berger_hodge_component_map import COMMAND_BUILDERS as BERGER_HODGE_COMMAND_BUILDERS, berger_hodge_component_report_to_markdown
from .rare_b_observable_map import rare_b_status_report, rare_b_status_to_markdown
from .b_to_s_mumu_operator_matching import b_to_s_mumu_status_report, b_to_s_mumu_status_to_markdown
from .rare_b_fcnc_generation_mechanism import rare_b_fcnc_generation_status_report, rare_b_fcnc_generation_status_to_markdown
from .unified_dynamical_action import unified_action_status_report, unified_action_status_to_markdown
from .physical_scale_generation import physical_scale_status_report, physical_scale_status_to_markdown
from .scalar_topographic_vacuum_action import scalar_topographic_vacuum_status_report, scalar_topographic_vacuum_status_to_markdown
from .scalar_topographic_profile_boundary_closure import profile_boundary_status_report, profile_boundary_status_to_markdown
from .absolute_unit_anchor_generation import absolute_unit_status_report, absolute_unit_status_to_markdown
from .pilot_wave_scale_modulus_dynamics import pilot_wave_status_report, pilot_wave_status_to_markdown
from .quantum_effective_action_casimir_backreaction import quantum_effective_action_status_report, quantum_effective_action_status_to_markdown
from .full_geometric_gauge_fixed_hessian import full_hessian_status_report, full_hessian_status_to_markdown
from .primordial_boundary_tension_action_source_closure import boundary_tension_status_report, boundary_tension_status_to_markdown
from .s7_fiber_integration_physical_localization import s7_fiber_integration_status_report, s7_fiber_integration_status_to_markdown


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


def _print_unicode(text: str) -> None:
    """Print UTF-8 reports on Windows consoles with legacy encodings."""
    try:
        print(text)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))


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
    bedrock_status = commands.add_parser("neutrino-bedrock-status", help="Show the neutrino bedrock/dynamic-layer doctrine")
    bedrock_status.add_argument("--format", choices=("markdown", "json"), default="json")
    completion_ledger = commands.add_parser("full-completion-ledger", help="Show the sixteen-category BHSM completion blocker ledger")
    completion_ledger.add_argument("--format", choices=("json",), default="json")
    completion_priority = commands.add_parser("full-completion-priority-map", help="Show predeclared completion-target scores")
    completion_priority.add_argument("--format", choices=("json",), default="json")
    completion_status = commands.add_parser("full-completion-status", help="Render the conservative BHSM full-completion status")
    completion_status.add_argument("--format", choices=("markdown", "json"), default="markdown")
    completion_target = commands.add_parser("full-completion-selected-target", help="Show the selected closure target and result")
    completion_target.add_argument("--format", choices=("json",), default="json")
    charged_source = commands.add_parser("charged-source-search", help="Inventory local charged action and mixing sources")
    charged_source.add_argument("--format", choices=("json",), default="json")
    charged_stiffness = commands.add_parser("charged-action-stiffness", help="Audit charged action and stiffness provenance")
    charged_stiffness.add_argument("--format", choices=("json",), default="json")
    eta_source = commands.add_parser("eta-l-source-audit", help="Audit the charged-lepton eta_l source")
    eta_source.add_argument("--format", choices=("json",), default="json")
    ckm_exponent = commands.add_parser("ckm-exponent-source-audit", help="Audit the CKM 1/16 exponent source")
    ckm_exponent.add_argument("--format", choices=("json",), default="json")
    charged_mixing = commands.add_parser("charged-mixing-law-audit", help="Audit charged mixing-law provenance")
    charged_mixing.add_argument("--format", choices=("json",), default="json")
    charged_dimensions = commands.add_parser("charged-dimensional-audit", help="Audit dimensions of charged closure formulas")
    charged_dimensions.add_argument("--format", choices=("json",), default="json")
    charged_report = commands.add_parser("charged-closure-report", help="Render the charged closure report")
    charged_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    common_source = commands.add_parser("common-16-source-search", help="Locate common-16 source artifacts")
    common_source.add_argument("--format", choices=("json",), default="json")
    common_incidence = commands.add_parser("common-16-incidence-audit", help="Audit exact common-16 incidence identities")
    common_incidence.add_argument("--format", choices=("json",), default="json")
    common_bridge = commands.add_parser("common-16-bridge-beta-audit", help="Audit common-16 bridge and beta identities")
    common_bridge.add_argument("--format", choices=("json",), default="json")
    common_transport = commands.add_parser("common-16-ckm-transport-audit", help="Audit the CKM reciprocal transport gate")
    common_transport.add_argument("--format", choices=("json",), default="json")
    common_provenance = commands.add_parser("common-16-provenance-audit", help="Apply common-16 provenance gates")
    common_provenance.add_argument("--format", choices=("json",), default="json")
    common_report = commands.add_parser("common-16-closure-report", help="Render the common-16 closure report")
    common_report.add_argument("--format", choices=("markdown", "json"), default="markdown")
    final_status = commands.add_parser("final-completion-status", help="Render the v1.8 conservative completion status")
    final_status.add_argument("--format", choices=("markdown", "json"), default="markdown")
    final_ledger = commands.add_parser("final-completion-ledger", help="Show the v1.8 completion blocker ledger")
    final_ledger.add_argument("--format", choices=("json",), default="json")
    hardening_commands = (
        "engine-status",
        "physics-status",
        "reviewer-reproduction",
        "engine-invariants",
        "minimal-theorem-core",
        "omega-f-action-audit",
        "rho-ch-action-audit",
        "falsification-table",
        "external-reproduction-packet",
    )
    for command in hardening_commands:
        hardening = commands.add_parser(command, help=f"Render the BHSM v1.9 {command} report")
        hardening.add_argument("--format", choices=("json", "markdown"), default="json")
    primitive_commands = (
        "primitive-charged-incidence",
        "rho-ch-gcd-selection",
        "overlap-4-over-3-source",
        "bridge-beta-identity",
        "ckm-log-transport-gate",
        "physical-normalization-gate",
        "external-reproduction-status",
        "primitive-charged-incidence-report",
    )
    for command in primitive_commands:
        primitive = commands.add_parser(command, help=f"Render the BHSM v2.0 {command} audit")
        primitive.add_argument("--format", choices=("json", "markdown"), default="json")
    action_lemma_commands = (
        "action-lemma-source-search",
        "primitive-lattice-rule",
        "maximal-overlap-bridge-rule",
        "log-transport-averaging",
        "ckm-log-transport-application",
        "action-lemma-closure-report",
    )
    for command in action_lemma_commands:
        lemma = commands.add_parser(command, help=f"Render the BHSM v2.1 {command} audit")
        lemma.add_argument("--format", choices=("json", "markdown"), default="json")
    ckm_channel_commands = (
        "ckm-channel-source-search",
        "ckm-channel-count-audit",
        "ckm-maximal-sector-selection",
        "ckm-channel-equivalence-report",
    )
    for command in ckm_channel_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v2.2 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    bidirectional_commands = (
        "ckm-bidirectional-source-search",
        "ckm-bidirectional-channel-count",
        "ckm-adjoint-pair-selection",
        "ckm-channel-alternative-resolution",
        "ckm-bidirectional-log-transport-application",
        "ckm-bidirectional-channel-report",
    )
    for command in bidirectional_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v2.3 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    normalized_action_adjoint_pair_commands = (
        "normalized-action-adjoint-pair-search",
        "normalized-action-adjoint-pair-selection",
        "hermitian-charged-current-rule",
        "ckm-transport-space-gate",
        "ckm-alternative-channel-blockers",
        "normalized-action-adjoint-pair-report",
    )
    for command in normalized_action_adjoint_pair_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v2.5 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    charged_current_action_commands = (
        "charged-current-action-search",
        "normalized-charged-current-action-term",
        "charged-current-transport-space",
        "hermitian-adjoint-pair-transport-gate",
        "ckm-transport-space-application-gate",
        "charged-current-action-report",
    )
    for command in charged_current_action_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v2.6 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    bounded_interface_commands = (
        "ckm-bounded-interface-search",
        "ckm-bounded-interface-term",
        "normalized-projector-sandwich",
        "projector-domain-codomain",
        "paired-term-normalization",
        "ckm-identification-gate",
        "ckm-transport-space-selection",
        "ckm-bounded-interface-report",
    )
    for command in bounded_interface_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v2.7 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    measure_commands = (
        "ckm-boundary-measure-search", "ckm-boundary-measure-source",
        "ckm-coefficient-normalization", "ckm-action-measure-coefficient-pair",
        "normalized-ckm-action-candidate", "ckm-projector-sandwich-requirement",
        "ckm-paired-normalization-rule", "ckm-transport-space-blocker",
        "ckm-boundary-measure-normalization-report",
    )
    for command in measure_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v2.8 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    coefficient_commands = ("ckm-coefficient-form-source-search","weak-charged-current-coefficient-form","g2-bh-source","alpha2-bh-source","weak-coupling-convention","ckm-coefficient-form","ckm-coefficient-value-source","ckm-measure-coefficient-attachment-v2-9","ckm-coefficient-form-report")
    for command in coefficient_commands:
        channel=commands.add_parser(command,help=f"Render the BHSM v2.9 {command} audit"); channel.add_argument("--format",choices=("json","markdown"),default="json")
    weak_gauge_commands = (
        "weak-gauge-action-source-search",
        "weak-gauge-algebra-source",
        "normalized-weak-gauge-action-skeleton",
        "weak-gauge-trace-normalization",
        "g2-bh-action-source",
        "alpha2-bh-action-source",
        "normalized-weak-gauge-action-coefficient",
        "ckm-value-source-blocker",
        "weak-gauge-action-source-report",
    )
    for command in weak_gauge_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v3.0 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    gauge_quantum_commands = (
        "gauge-coupling-quantum-search",
        "gauge-coupling-registry-pattern",
        "gauge-coupling-volume-denominator",
        "gauge-sector-weight-source",
        "universal-gauge-coupling-quantum",
        "gauge-coupling-action-attachment",
        "alpha-i-action-derivation",
        "g2-action-source-update",
        "ckm-value-source-update",
        "gauge-coupling-quantum-report",
    )
    for command in gauge_quantum_commands:
        channel = commands.add_parser(command, help=f"Render the BHSM v3.1 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    for command in FULL_ACTION_COMMAND_BUILDERS:
        channel = commands.add_parser(command, help=f"Render the BHSM v4.0 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    for command in BOUNDARY_MEASURE_COMMAND_BUILDERS:
        channel = commands.add_parser(command, help=f"Render the BHSM v4.1 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    for command in BERGER_FRAME_COMMAND_BUILDERS:
        channel = commands.add_parser(command, help=f"Render the BHSM v4.2 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    for command in GAUGE_COFRAME_COMMAND_BUILDERS:
        channel = commands.add_parser(command, help=f"Render the BHSM v4.3 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    for command in BERGER_HODGE_COMMAND_BUILDERS:
        channel = commands.add_parser(command, help=f"Render the BHSM v4.4 {command} audit")
        channel.add_argument("--format", choices=("json", "markdown"), default="json")
    rare_b = commands.add_parser("rare-b-observable-map-status", help="Render the BHSM v5.1 rare-B observable-map scaffold")
    rare_b.add_argument("--format", choices=("json", "markdown"), default="json")
    b_to_s = commands.add_parser("b-to-s-mumu-operator-matching-status", help="Render the BHSM v5.2 b -> s mu+ mu- operator-matching kill screen")
    b_to_s.add_argument("--format", choices=("json", "markdown"), default="json")
    fcnc = commands.add_parser("rare-b-fcnc-generation-status", help="Render the BHSM v5.3 rare-B FCNC generation-mechanism kill screen")
    fcnc.add_argument("--format", choices=("json", "markdown"), default="json")
    unified = commands.add_parser("unified-dynamical-action-status", help="Render the BHSM v5.4 unified dynamical action construction")
    unified.add_argument("--format", choices=("json", "markdown"), default="json")
    scale = commands.add_parser("physical-scale-generation-status", help="Render the BHSM v5.5 physical-scale generation construction")
    scale.add_argument("--format", choices=("json", "markdown"), default="json")
    scalar_vacuum = commands.add_parser("scalar-topographic-vacuum-status", help="Render the BHSM v5.6 scalar/topographic vacuum action derivation")
    scalar_vacuum.add_argument("--format", choices=("json", "markdown"), default="json")
    scalar_profile = commands.add_parser("scalar-topographic-profile-boundary-status", help="Render the BHSM v5.7 scalar/topographic profile and boundary closure")
    scalar_profile.add_argument("--format", choices=("json", "markdown"), default="json")
    absolute_unit = commands.add_parser("absolute-unit-anchor-status", help="Render the BHSM v5.8 absolute unit-anchor generation audit")
    absolute_unit.add_argument("--format", choices=("json", "markdown"), default="json")
    pilot_wave = commands.add_parser("pilot-wave-scale-modulus-status", help="Render the BHSM v5.9 pilot-wave scale-modulus dynamics")
    pilot_wave.add_argument("--format", choices=("json", "markdown"), default="json")
    quantum_effective = commands.add_parser("quantum-effective-action-status", help="Render the BHSM v5.10 quantum-effective-action and Casimir-backreaction audit")
    quantum_effective.add_argument("--format", choices=("json", "markdown"), default="json")
    full_hessian = commands.add_parser("full-geometric-gauge-fixed-hessian-status", help="Render the BHSM v5.11 full quadratic-operator audit")
    full_hessian.add_argument("--format", choices=("json", "markdown"), default="json")
    boundary_tension = commands.add_parser("primordial-boundary-tension-status", help="Render the BHSM v5.12 primordial boundary-tension source audit")
    boundary_tension.add_argument("--format", choices=("json", "markdown"), default="json")
    s7_fiber = commands.add_parser("s7-fiber-integration-status", help="Render the BHSM v6.0 S7 fiber-integration and physical-localization audit")
    s7_fiber.add_argument("--format", choices=("json", "markdown"), default="json")
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
    if args.command == "neutrino-bedrock-status":
        report = load_neutrino_bedrock_status()
        if args.format == "markdown":
            print(neutrino_bedrock_status_to_markdown(report), end="")
        else:
            print(json.dumps(report, indent=2, sort_keys=True))
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
    if args.command == "charged-source-search":
        print(json.dumps(search_charged_closure_sources().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "charged-action-stiffness":
        print(json.dumps(derive_or_locate_charged_action_stiffness().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "eta-l-source-audit":
        print(json.dumps(derive_or_locate_eta_l_source().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "ckm-exponent-source-audit":
        print(json.dumps(derive_or_locate_ckm_exponent_source().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "charged-mixing-law-audit":
        print(json.dumps(derive_or_locate_charged_mixing_law_source().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "charged-dimensional-audit":
        print(json.dumps(audit_charged_closure_dimensions().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "charged-closure-report":
        report = build_charged_closure_report()
        if args.format == "markdown":
            print(charged_closure_report_to_markdown(report), end="")
        else:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "common-16-source-search":
        print(json.dumps(search_common_16_sources().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "common-16-incidence-audit":
        print(json.dumps(audit_common_16_incidence().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "common-16-bridge-beta-audit":
        print(json.dumps(audit_common_16_bridge_beta().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "common-16-ckm-transport-audit":
        print(json.dumps(audit_common_16_ckm_transport().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "common-16-provenance-audit":
        print(json.dumps(audit_common_16_provenance().to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command in ("common-16-closure-report", "final-completion-status"):
        report = build_final_completion_report()
        if args.format == "markdown":
            print(final_completion_report_to_markdown(report), end="")
        else:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "final-completion-ledger":
        report = build_final_completion_report()
        print(json.dumps({
            "version": report.version,
            "full_completion_claimed": report.completion_claimed,
            "selected_target": report.target_selection.selected_target,
            "open_blockers": list(report.provenance.open_blockers),
            "legacy_blockers": [row.to_dict() for row in build_full_completion_blocker_ledger()],
        }, indent=2, sort_keys=True))
        return 0
    if args.command in {
        "engine-status",
        "physics-status",
        "reviewer-reproduction",
        "engine-invariants",
        "minimal-theorem-core",
        "omega-f-action-audit",
        "rho-ch-action-audit",
        "falsification-table",
        "external-reproduction-packet",
    }:
        emit_hardening_payload(args.command, args.format)
        return 0
    if args.command in {
        "action-lemma-source-search",
        "primitive-lattice-rule",
        "maximal-overlap-bridge-rule",
        "log-transport-averaging",
        "ckm-log-transport-application",
        "action-lemma-closure-report",
    }:
        builders = {
            "action-lemma-source-search": search_action_lemma_sources,
            "primitive-lattice-rule": audit_primitive_lattice_rule,
            "maximal-overlap-bridge-rule": audit_maximal_overlap_bridge_rule,
            "log-transport-averaging": lambda: prove_log_transport_averaging(16),
            "ckm-log-transport-application": audit_ckm_channel_application,
            "action-lemma-closure-report": build_action_lemma_closure_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {
        "ckm-channel-source-search",
        "ckm-channel-count-audit",
        "ckm-maximal-sector-selection",
        "ckm-channel-equivalence-report",
    }:
        builders = {
            "ckm-channel-source-search": search_ckm_channel_sources,
            "ckm-channel-count-audit": audit_ckm_channel_counts,
            "ckm-maximal-sector-selection": audit_maximal_sector_selection,
            "ckm-channel-equivalence-report": build_ckm_channel_equivalence_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {
        "ckm-bidirectional-source-search",
        "ckm-bidirectional-channel-count",
        "ckm-adjoint-pair-selection",
        "ckm-channel-alternative-resolution",
        "ckm-bidirectional-log-transport-application",
        "ckm-bidirectional-channel-report",
    }:
        builders = {
            "ckm-bidirectional-source-search": search_ckm_bidirectional_sources,
            "ckm-bidirectional-channel-count": audit_bidirectional_channel_count,
            "ckm-adjoint-pair-selection": audit_ckm_adjoint_pair_selection,
            "ckm-channel-alternative-resolution": audit_ckm_channel_alternative_resolution,
            "ckm-bidirectional-log-transport-application": audit_bidirectional_log_transport_application,
            "ckm-bidirectional-channel-report": build_ckm_bidirectional_channel_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {
        "normalized-action-adjoint-pair-search",
        "normalized-action-adjoint-pair-selection",
        "hermitian-charged-current-rule",
        "ckm-transport-space-gate",
        "ckm-alternative-channel-blockers",
        "normalized-action-adjoint-pair-report",
    }:
        builders = {
            "normalized-action-adjoint-pair-search": search_normalized_action_adjoint_pair_sources,
            "normalized-action-adjoint-pair-selection": audit_normalized_action_adjoint_pair_selection,
            "hermitian-charged-current-rule": audit_hermitian_charged_current_action_rule,
            "ckm-transport-space-gate": audit_ckm_transport_space_gate,
            "ckm-alternative-channel-blockers": audit_ckm_alternative_channel_blockers,
            "normalized-action-adjoint-pair-report": build_normalized_action_adjoint_pair_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.command == "normalized-action-adjoint-pair-report":
            print(normalized_action_adjoint_pair_report_to_markdown(payload))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {
        "charged-current-action-search",
        "normalized-charged-current-action-term",
        "charged-current-transport-space",
        "hermitian-adjoint-pair-transport-gate",
        "ckm-transport-space-application-gate",
        "charged-current-action-report",
    }:
        builders = {
            "charged-current-action-search": search_charged_current_action_sources,
            "normalized-charged-current-action-term": audit_normalized_charged_current_action_term,
            "charged-current-transport-space": audit_charged_current_transport_space,
            "hermitian-adjoint-pair-transport-gate": audit_hermitian_adjoint_pair_transport_gate,
            "ckm-transport-space-application-gate": audit_ckm_transport_space_application_gate,
            "charged-current-action-report": build_charged_current_action_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.command == "charged-current-action-report":
            print(charged_current_action_report_to_markdown(payload))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {
        "ckm-bounded-interface-search",
        "ckm-bounded-interface-term",
        "normalized-projector-sandwich",
        "projector-domain-codomain",
        "paired-term-normalization",
        "ckm-identification-gate",
        "ckm-transport-space-selection",
        "ckm-bounded-interface-report",
    }:
        builders = {
            "ckm-bounded-interface-search": search_ckm_bounded_interface_sources,
            "ckm-bounded-interface-term": audit_ckm_bounded_interface_term,
            "normalized-projector-sandwich": audit_normalized_projector_sandwich,
            "projector-domain-codomain": audit_projector_domain_codomain,
            "paired-term-normalization": audit_paired_term_normalization,
            "ckm-identification-gate": audit_ckm_identification_gate,
            "ckm-transport-space-selection": audit_ckm_transport_space_selection,
            "ckm-bounded-interface-report": build_ckm_bounded_interface_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.command == "ckm-bounded-interface-report":
            print(ckm_bounded_interface_report_to_markdown(payload))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {
        "ckm-boundary-measure-search", "ckm-boundary-measure-source",
        "ckm-coefficient-normalization", "ckm-action-measure-coefficient-pair",
        "normalized-ckm-action-candidate", "ckm-projector-sandwich-requirement",
        "ckm-paired-normalization-rule", "ckm-transport-space-blocker",
        "ckm-boundary-measure-normalization-report",
    }:
        builders = {
            "ckm-boundary-measure-search": search_boundary_measure_normalization_sources,
            "ckm-boundary-measure-source": audit_boundary_measure_source,
            "ckm-coefficient-normalization": audit_coefficient_normalization,
            "ckm-action-measure-coefficient-pair": audit_measure_coefficient_pair,
            "normalized-ckm-action-candidate": audit_normalized_ckm_action_candidate,
            "ckm-projector-sandwich-requirement": audit_projector_sandwich_requirement,
            "ckm-paired-normalization-rule": audit_paired_normalization_rule,
            "ckm-transport-space-blocker": audit_transport_space_blocker,
            "ckm-boundary-measure-normalization-report": build_boundary_measure_normalization_report,
        }
        payload = builders[args.command]()
        if args.format == "json": print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.command == "ckm-boundary-measure-normalization-report": print(boundary_measure_normalization_report_to_markdown(payload))
        else: print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {"ckm-coefficient-form-source-search","weak-charged-current-coefficient-form","g2-bh-source","alpha2-bh-source","weak-coupling-convention","ckm-coefficient-form","ckm-coefficient-value-source","ckm-measure-coefficient-attachment-v2-9","ckm-coefficient-form-report"}:
        builders={"ckm-coefficient-form-source-search":search_coefficient_form_sources,"weak-charged-current-coefficient-form":audit_weak_charged_current_form,"g2-bh-source":audit_g2_source,"alpha2-bh-source":audit_alpha2_source,"weak-coupling-convention":audit_weak_coupling_convention,"ckm-coefficient-form":audit_ckm_coefficient_form,"ckm-coefficient-value-source":audit_ckm_coefficient_value_source,"ckm-measure-coefficient-attachment-v2-9":audit_measure_coefficient_attachment,"ckm-coefficient-form-report":build_coefficient_form_report}
        payload=builders[args.command]()
        if args.format=="json": print(json.dumps(payload,indent=2,sort_keys=True))
        elif args.command=="ckm-coefficient-form-report": print(coefficient_form_report_to_markdown(payload))
        else: print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload,indent=2,sort_keys=True)}\n```")
        return 0
    if args.command in {
        "weak-gauge-action-source-search",
        "weak-gauge-algebra-source",
        "normalized-weak-gauge-action-skeleton",
        "weak-gauge-trace-normalization",
        "g2-bh-action-source",
        "alpha2-bh-action-source",
        "normalized-weak-gauge-action-coefficient",
        "ckm-value-source-blocker",
        "weak-gauge-action-source-report",
    }:
        builders = {
            "weak-gauge-action-source-search": search_weak_gauge_action_sources,
            "weak-gauge-algebra-source": audit_weak_gauge_algebra_source,
            "normalized-weak-gauge-action-skeleton": audit_normalized_weak_gauge_action_skeleton,
            "weak-gauge-trace-normalization": audit_weak_gauge_trace_normalization,
            "g2-bh-action-source": audit_g2_bh_action_source,
            "alpha2-bh-action-source": audit_alpha2_bh_action_source,
            "normalized-weak-gauge-action-coefficient": audit_normalized_weak_gauge_action_coefficient,
            "ckm-value-source-blocker": audit_ckm_value_source_blocker,
            "weak-gauge-action-source-report": build_weak_gauge_action_source_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif args.command == "weak-gauge-action-source-report":
            print(weak_gauge_action_source_report_to_markdown(payload))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
        return 0
    if args.command in {
        "gauge-coupling-quantum-search",
        "gauge-coupling-registry-pattern",
        "gauge-coupling-volume-denominator",
        "gauge-sector-weight-source",
        "universal-gauge-coupling-quantum",
        "gauge-coupling-action-attachment",
        "alpha-i-action-derivation",
        "g2-action-source-update",
        "ckm-value-source-update",
        "gauge-coupling-quantum-report",
    }:
        builders = {
            "gauge-coupling-quantum-search": search_gauge_coupling_quantum_sources,
            "gauge-coupling-registry-pattern": audit_gauge_coupling_registry_pattern,
            "gauge-coupling-volume-denominator": audit_gauge_coupling_volume_denominator,
            "gauge-sector-weight-source": audit_gauge_sector_weight_source,
            "universal-gauge-coupling-quantum": audit_universal_gauge_coupling_quantum,
            "gauge-coupling-action-attachment": audit_gauge_coupling_action_attachment,
            "alpha-i-action-derivation": audit_alpha_i_action_derivation,
            "g2-action-source-update": audit_g2_action_source_update,
            "ckm-value-source-update": audit_ckm_value_source_update,
            "gauge-coupling-quantum-report": build_gauge_coupling_quantum_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        elif args.command == "gauge-coupling-quantum-report":
            _print_unicode(gauge_coupling_quantum_report_to_markdown(payload))
        else:
            body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{body}\n```")
        return 0
    if args.command in FULL_ACTION_COMMAND_BUILDERS:
        payload = FULL_ACTION_COMMAND_BUILDERS[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        elif args.command == "full-action-closure-report":
            _print_unicode(full_action_closure_report_to_markdown(payload))
        else:
            body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
            _print_unicode(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{body}\n```")
        return 0
    if args.command in BOUNDARY_MEASURE_COMMAND_BUILDERS:
        payload = BOUNDARY_MEASURE_COMMAND_BUILDERS[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        elif args.command == "boundary-collar-measure-report":
            _print_unicode(boundary_collar_measure_report_to_markdown(payload))
        else:
            body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
            _print_unicode(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{body}\n```")
        return 0
    if args.command in BERGER_FRAME_COMMAND_BUILDERS:
        payload = BERGER_FRAME_COMMAND_BUILDERS[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        elif args.command == "berger-frame-weighting-report":
            _print_unicode(berger_frame_weighting_report_to_markdown(payload))
        else:
            body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
            _print_unicode(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{body}\n```")
        return 0
    if args.command in GAUGE_COFRAME_COMMAND_BUILDERS:
        payload = GAUGE_COFRAME_COMMAND_BUILDERS[args.command]()
        if args.format == "json": print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        elif args.command == "gauge-coframe-hodge-report": _print_unicode(gauge_coframe_hodge_report_to_markdown(payload))
        else: _print_unicode(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)}\n```")
        return 0
    if args.command in BERGER_HODGE_COMMAND_BUILDERS:
        payload = BERGER_HODGE_COMMAND_BUILDERS[args.command]()
        if args.format == "json": print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        elif args.command == "berger-hodge-component-report": _print_unicode(berger_hodge_component_report_to_markdown(payload))
        else: _print_unicode(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)}\n```")
        return 0
    if args.command == "rare-b-observable-map-status":
        payload = rare_b_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(rare_b_status_to_markdown(payload))
        return 0
    if args.command == "b-to-s-mumu-operator-matching-status":
        payload = b_to_s_mumu_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(b_to_s_mumu_status_to_markdown(payload))
        return 0
    if args.command == "rare-b-fcnc-generation-status":
        payload = rare_b_fcnc_generation_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(rare_b_fcnc_generation_status_to_markdown(payload))
        return 0
    if args.command == "unified-dynamical-action-status":
        payload = unified_action_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(unified_action_status_to_markdown(payload))
        return 0
    if args.command == "physical-scale-generation-status":
        payload = physical_scale_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(physical_scale_status_to_markdown(payload))
        return 0
    if args.command == "scalar-topographic-vacuum-status":
        payload = scalar_topographic_vacuum_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(scalar_topographic_vacuum_status_to_markdown(payload))
        return 0
    if args.command == "scalar-topographic-profile-boundary-status":
        payload = profile_boundary_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(profile_boundary_status_to_markdown(payload))
        return 0
    if args.command == "absolute-unit-anchor-status":
        payload = absolute_unit_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(absolute_unit_status_to_markdown(payload))
        return 0
    if args.command == "pilot-wave-scale-modulus-status":
        payload = pilot_wave_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(pilot_wave_status_to_markdown(payload))
        return 0
    if args.command == "quantum-effective-action-status":
        payload = quantum_effective_action_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(quantum_effective_action_status_to_markdown(payload))
        return 0
    if args.command == "full-geometric-gauge-fixed-hessian-status":
        payload = full_hessian_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(full_hessian_status_to_markdown(payload))
        return 0
    if args.command == "primordial-boundary-tension-status":
        payload = boundary_tension_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(boundary_tension_status_to_markdown(payload))
        return 0
    if args.command == "s7-fiber-integration-status":
        payload = s7_fiber_integration_status_report()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            _print_unicode(s7_fiber_integration_status_to_markdown(payload))
        return 0
    if args.command in {
        "primitive-charged-incidence",
        "rho-ch-gcd-selection",
        "overlap-4-over-3-source",
        "bridge-beta-identity",
        "ckm-log-transport-gate",
        "physical-normalization-gate",
        "external-reproduction-status",
        "primitive-charged-incidence-report",
    }:
        builders = {
            "primitive-charged-incidence": build_primitive_charged_incidence_report,
            "rho-ch-gcd-selection": audit_rho_gcd_selection,
            "overlap-4-over-3-source": audit_overlap_4_over_3,
            "bridge-beta-identity": audit_bridge_beta_identity,
            "ckm-log-transport-gate": audit_ckm_log_transport,
            "physical-normalization-gate": audit_physical_normalization,
            "external-reproduction-status": audit_external_reproduction_status,
            "primitive-charged-incidence-report": build_primitive_charged_incidence_report,
        }
        payload = builders[args.command]()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"# {args.command.replace('-', ' ').title()}\n\n```json\n{json.dumps(payload, indent=2, sort_keys=True)}\n```")
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
