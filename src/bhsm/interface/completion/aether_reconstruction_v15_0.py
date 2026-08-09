"""Operator/domain reconstruction predicates for BHSM v15.0."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .aether_parent_stratification_v15_0 import AetherState, CORE_STRATUM, GEOMETRIC_STRATUM


@dataclass(frozen=True)
class ReconstructionEvidence:
    self_adjoint_domain: bool
    bounded_commutators_on_dense_algebra: bool
    full_rank_principal_symbol: bool
    bhsm_spectral_dimension: bool
    boundary_domain_compatible: bool
    continuum_trace_realization_valid: bool
    regular_support_formula_recovered: bool


def reconstruction_predicate(state: AetherState, evidence: ReconstructionEvidence | None) -> str:
    if state.stratum == CORE_STRATUM or evidence is None:
        return "NONRECONSTRUCTIBLE_AETHER_STATE"
    required = (
        evidence.self_adjoint_domain,
        evidence.bounded_commutators_on_dense_algebra,
        evidence.full_rank_principal_symbol,
        evidence.bhsm_spectral_dimension,
        evidence.boundary_domain_compatible,
        evidence.continuum_trace_realization_valid,
        evidence.regular_support_formula_recovered,
    )
    return "RECONSTRUCTIBLE_BHSM_GEOMETRY" if all(required) else "NONRECONSTRUCTIBLE_AETHER_STATE"


def edge_spectral_distance(dirac_edge_magnitude: float) -> float:
    magnitude = float(dirac_edge_magnitude)
    if magnitude <= 0.0:
        raise ValueError("edge magnitude must be positive")
    return 1.0 / magnitude


def reconstruction_payload() -> dict[str, Any]:
    complete = ReconstructionEvidence(True, True, True, True, True, True, True)
    blocked_trace = ReconstructionEvidence(True, True, True, True, False, False, True)
    return {
        "version": "v15.0",
        "predicate": "Rec(A)=all declared operator/domain reconstruction conditions",
        "regular_complete_evidence": asdict(complete),
        "regular_complete_result": "RECONSTRUCTIBLE_BHSM_GEOMETRY",
        "v14_64_naive_L2_diamond_evidence": asdict(blocked_trace),
        "v14_64_naive_L2_diamond_result": "NONRECONSTRUCTIBLE_AETHER_STATE",
        "v14_64_trace_domain_obstruction_preserved": True,
        "naive_finite_diamond_promoted_to_continuum_operator": False,
        "distance_rule_reused": "edge_restricted_Connes_distance=1/abs(D_ij)",
        "global_continuum_Connes_metric_claimed": False,
        "distance_on_regular_reconstructible_domain": "defined_when_Lipschitz_ball_and_self_adjoint_domain_close",
        "distance_on_core": None,
        "core_size": None,
        "infinite_Haar_depth_vs_absent_core_distance": "DISTINCT",
        "singularity_as_reconstruction_failure": "HYPOTHESIS_NOT_THEOREM",
        "continuous_geometricity_field_introduced": False,
    }


def high_excitation_counterexample() -> dict[str, Any]:
    """Logical independence witness: excitation can vary while Rec stays true."""
    return {
        "state_low": {"dimensionless_excitation": 1, "Rec": True},
        "state_high": {"dimensionless_excitation": 2, "Rec": True},
        "monotone_high_excitation_implies_lower_reconstructibility_derived": False,
        "classification": "UNDERDETERMINED_BY_CURRENT_BHSM",
        "missing_coupling": "action_owned_coupling_between_transition_generator_and_reconstruction_defect_or_domain_loss",
        "empirical_inputs_used": False,
    }
