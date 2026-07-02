"""Bounded source inventory for the v3.0 weak gauge audit."""

from .common import STATUS_SKELETON, input_guard


def search_weak_gauge_action_sources() -> dict[str, object]:
    return {
        "files_scanned": "v3.0 bounded repository search paths",
        "hits": ["theory/finite_boundary_algebra_source_gate.md", "theory/derived_normalized_gauge_action_skeleton.md", "theory/theorem_discharge_boundary_trace_normalization.md", "artifacts/BHSM_minimal_runtime_parameter_requirements_v1_2.json", "src/gauge_couplings.py"],
        "weak_algebra_evidence": ["conditional M2(C) active weak block"],
        "gauge_action_skeleton_evidence": ["conditional normalized relative kinetic skeleton"],
        "trace_normalization_evidence": ["K1=10/3, K2=K3=2, eta_Y=3/5"],
        "g2_runtime_evidence": ["g2_BH_runtime explicitly required"],
        "g2_action_evidence": [],
        "alpha2_registered_evidence": ["alpha_2 registered geometric screen"],
        "alpha2_action_evidence": [],
        "weak_convention_evidence": ["g2^2/(4*pi)=alpha2 convention only"],
        "bridge_arithmetic_evidence": ["no action identification; rejected as coupling source"],
        "evidence_against_action_derivation": ["overall k unfixed", "measured coupling theorem explicitly open"],
        "missing_sources": ["overall weak kinetic coefficient", "action-derived g2_BH or alpha2_BH", "physical measure normalization"],
        "status": STATUS_SKELETON,
        **input_guard(),
    }
