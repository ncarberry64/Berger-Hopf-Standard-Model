"""Materialize the maximal local GFHS germ and its exact global blocker."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from bhsm.interface.background_covariant_gfhs_operator_family import (
    ACTION_VERSION,
    CLASSIFICATION,
    EXACT_BLOCKER,
    STATUS,
    ae2_to_ae4_transport_diagram,
    background_mixed_derivative_witness,
    child_inheritance_status,
    claim_boundary,
    critical_reductions,
    event_balance_residual,
    relative_boundary_graph_nonuniqueness_witness,
    representation_validation,
    source_reconstruction,
    stratified_action_composition,
)


TARGET = ROOT / "artifacts/action_extension/BHSM_BACKGROUND_COVARIANT_GFHS_OPERATOR_FAMILY.json"
SCRIPT = Path(__file__).resolve()
MODULE = ROOT / "src/bhsm/interface/background_covariant_gfhs_operator_family.py"
THEORY = ROOT / "theory/bhsm_background_covariant_gfhs_operator_family.md"
TEST = ROOT / "tests/test_background_covariant_gfhs_operator_family.py"


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json", ".toml", ".yaml", ".yml"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite artifact value")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_payload() -> dict[str, Any]:
    sources = source_reconstruction()
    representation = representation_validation()
    geometry = background_mixed_derivative_witness()
    transport = ae2_to_ae4_transport_diagram()
    inheritance = child_inheritance_status()
    balance = event_balance_residual()
    nonuniqueness = relative_boundary_graph_nonuniqueness_witness()
    reductions = critical_reductions()
    composition = stratified_action_composition()
    claims = claim_boundary()
    source_paths = {
        row.source
        for row in sources
        if row.source != "NO_RETAINED_MACHINE_READABLE_SOURCE"
    }
    source_paths.update(
        {
            str(MODULE.relative_to(ROOT)).replace("\\", "/"),
            str(SCRIPT.relative_to(ROOT)).replace("\\", "/"),
            str(THEORY.relative_to(ROOT)).replace("\\", "/"),
            str(TEST.relative_to(ROOT)).replace("\\", "/"),
        }
    )
    hashes = {
        relative: _sha256(ROOT / relative)
        for relative in sorted(source_paths)
        if (ROOT / relative).is_file()
    }
    validation = {
        "all_retained_sources_classified": all(row.classification.value for row in sources),
        "derived_responses_not_used_as_action_sources": not any(
            row.used_in_local_germ and row.classification.value == "DERIVED_RESPONSE"
            for row in sources
        ),
        "representation_generators_close": (
            representation["all_generators_Hermitian_residual"] < 1.0e-12
            and representation["SU2_commutator_residual"] < 1.0e-12
            and representation["SU3_commutator_residual"] < 1.0e-12
        ),
        "projectors_and_HS_hypercharge_preserved": (
            representation["family_projector_commutator_residual"] < 1.0e-12
            and max(representation["HS_incidence_hypercharge_covariance_residuals"]) < 1.0e-12
        ),
        "two_background_dependence_witnesses_nontrivial": geometry[
            "local_background_dependence_verified"
        ],
        "mixed_derivatives_match_direct_differentiation": max(
            geometry["direct_difference_residuals"].values()
        ) < 2.0e-8,
        "fermion_family_transport_commutes": transport[
            "fermion_family_intertwining_residual"
        ] < 1.0e-12,
        "boundary_graph_nonuniqueness_exact": (
            nonuniqueness["same_zero_field_match"]
            and nonuniqueness["different_nonzero_field_actions"]
            and nonuniqueness["reference_graph_operator_difference_norm"] == 0.0
            and nonuniqueness["first_field_jet_difference_norm"] > 0.0
        ),
        "event_balance_identity_reused_without_physical_promotion": (
            balance["algebraic_event_canonical_flux_balance_norm"] < 1.0e-12
            and balance["physical_event_balance_residual"] is None
            and not balance["physical_event_promotion"]
        ),
        "zero_reference_reduction": reductions["zero_reference_subtracted"],
        "no_empirical_input": not claims["empirical_inputs_used"],
        "global_family_not_overclaimed": (
            not claims["generating_family_exists"]
            and not claims["arbitrary_global_BHSM_background_accepted"]
        ),
        "gate7_claim_boundary_preserved": (
            not claims["physical_background_bound"]
            and not claims["physical_HS_direction_derived"]
            and not claims["physical_yukawas_derived"]
            and not claims["physical_spectrum_derived"]
            and not claims["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_BACKGROUND_COVARIANT_GFHS_OPERATOR_FAMILY",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "generating_family_exists": False,
        "local_current_C2_generating_germ_exists": True,
        "arbitrary_background_accepted": False,
        "arbitrary_regular_local_current_C2_background_accepted": True,
        "strata_domain_owned": composition,
        "gauge_action_source": "PARENT_MAXWELL_RADIAL_FORM__LOCAL_GALERKIN_SCHUR_ACTION_EXECUTABLE",
        "ghost_action_source": "SAME_MAXWELL_GAUGE_FUNCTIONAL_DERIVATIVE__LOCAL_FP_OPERATOR_EXECUTABLE",
        "fermion_action_source": "FOUNDATIONAL_ETA_DIRAC_ACTION__FREE_WEYL_AND_REPRESENTATION_CONNECTION_GERM_EXECUTABLE",
        "HS_action_source": "LOCAL_COEFFICIENT_FREE_EINSTEIN_CARTAN_HS_REWRITE_EXECUTABLE",
        "interaction_sources": {
            "gauge_fermion": "RANK16_REPRESENTATION_CONNECTION__GENERATED",
            "gauge_HS": "NOT_ACTION_OWNED_IN_FOUR_CHANNEL_AMPLITUDE_REDUCTION",
            "fermion_HS": "LOCAL_EC_UNIT_LR_INCIDENCE__GENERATED_NOT_PHYSICAL_YUKAWA",
            "quark_absolute_intrinsic_Yukawa": "NOT_DERIVED_AND_NOT_INSERTED",
        },
        "source_to_action_reconstruction": [row.to_dict() for row in sources],
        "representation_and_covariance": representation,
        "geometry_mixed_derivatives": geometry,
        "derivative_readiness": {
            "S1": "LOCAL_GERM_ACTION_DERIVED",
            "S2": "LOCAL_GERM_ACTION_DERIVED_WITH_GRADED_ODD_BLOCKS",
            "S3": "LOCAL_GERM_MATRIX_FREE_DIRECTIONAL_AD",
            "S4": "LOCAL_GERM_MATRIX_FREE_DIRECTIONAL_AD",
            "global_S1_S2_S3_S4": "BLOCKED_BY_NONFERMION_RELATIVE_BOUNDARY_GRAPH_FIRST_FIELD_JET",
            "dense_S3_or_S4_materialized": False,
        },
        "AE2_to_AE4_transport_diagram_status": transport,
        "event_child_inheritance_status": inheritance,
        "Noether_Hamiltonian_balance_status": balance,
        "critical_reductions": reductions,
        "irreducible_source_nonuniqueness_witness": nonuniqueness,
        "empirical_inputs_used": [],
        "physical_background_bound": False,
        "physical_HS_direction_derived": False,
        "physical_yukawas_derived": False,
        "physical_spectrum_derived": False,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "invalidated": [
            "USE_ZERO_BACKGROUND_RESPONSE_TABLES_AS_GENERATING_ACTION",
            "INSERT_FROZEN_BERGER_LEVELS_AS_FREE_FERMION_MASSES",
            "PROMOTE_LOCAL_EC_HS_UNIT_VERTICES_TO_PHYSICAL_YUKAWAS",
            "GUESS_A_NONFERMION_SEAM_OR_EVENT_CHILD_GRAPH",
            "CLAIM_GLOBAL_AE2_TO_AE4_COMMUTATION_FROM_DIMENSION_MATCHING",
        ],
        "open_blockers": [EXACT_BLOCKER],
        "exact_next_calculation": (
            "DERIVE_FROM_THE_RETAINED_BULK_VARIATION_THE_OPERATOR_VALUED_"
            "NONFERMION_RELATIVE_BOUNDARY_GRAPH_THETA_GFHS[B;A,c,cbar,H]_"
            "AND_COMPUTE_D_PhiSM_THETA_GFHS_AT_THE_REFERENCE_SLICE;_THEN_"
            "INSERT_THAT_GRAPH_IN_THE_AE4_RETARDED_DIRECT_SUM_AND_REEVALUATE_"
            "THE_PHYSICAL_EVENT_BALANCE_RESIDUAL"
        ),
        "hindsight": {
            "VALIDATED": [
                "MAXIMAL_REGULAR_CURRENT_C2_GFHS_LOCAL_GENERATING_GERM",
                "ACTION_DERIVED_LOCAL_S1_S2_S3_S4",
                "GENUINE_LOCAL_BACKGROUND_MIXED_DERIVATIVES",
                "FERMION_AND_FAMILY_AE2_TO_AE3_INTERTWINING",
                "ALGEBRAIC_EVENT_NOETHER_BALANCE_IDENTITY",
            ],
            "INVALIDATED": [
                "RESPONSE_TO_ACTION_PROMOTION",
                "FREE_INTERNAL_BERGER_LEVEL_AS_SM_MASS",
                "ZERO_FIELD_MATCH_AS_NONZERO_FIELD_DOMAIN_AUTHORITY",
            ],
            "OPEN": [EXACT_BLOCKER],
            "EXACT_NEXT_OBJECT": (
                "D_PhiSM_THETA_GFHS[B;0]_ON_GAUGE_GHOST_HS_RESET_TRACES"
            ),
        },
        "claims": claims,
        "source_sha256": hashes,
    }


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
