"""Materialize the GFHS reset generating-functional adjudication."""

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

from bhsm.interface.reset_boundary_generating_functional_adjudication import (
    ACTION_VERSION,
    CLASSIFICATION,
    EXACT_MISSING_DATUM,
    STATUS,
    actual_reset_map_ledger,
    boundary_phase_space_contract,
    brst_reset_compatibility,
    canonicality_adjudication,
    child_inheritance_status,
    claim_boundary,
    event_balance_status,
    exactness_adjudication,
    graph_and_global_derivative_status,
    hs_reset_adjudication,
    reference_canonicality_witness,
    source_search_ledger,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_RESET_BOUNDARY_GENERATING_FUNCTIONAL_ADJUDICATION.json"
)
SCRIPT = Path(__file__).resolve()
MODULE = ROOT / (
    "src/bhsm/interface/reset_boundary_generating_functional_adjudication.py"
)
THEORY = ROOT / "theory/bhsm_reset_boundary_generating_functional_adjudication.md"
TEST = ROOT / "tests/test_reset_boundary_generating_functional_adjudication.py"


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
    if isinstance(value, np.ndarray):
        return _canonical(value.tolist())
    if isinstance(value, np.complexfloating):
        value = complex(value)
    if isinstance(value, complex):
        if not (math.isfinite(value.real) and math.isfinite(value.imag)):
            raise ValueError("non-finite artifact value")
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
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
    phase = boundary_phase_space_contract()
    sources = source_search_ledger()
    reset = actual_reset_map_ledger()
    reference = reference_canonicality_witness()
    canonicality = canonicality_adjudication()
    exactness = exactness_adjudication()
    brst = brst_reset_compatibility()
    hs = hs_reset_adjudication()
    graph = graph_and_global_derivative_status()
    balance = event_balance_status()
    inheritance = child_inheritance_status()
    claims = claim_boundary()
    source_paths = (
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
        "src/bhsm/interface/ae31_c2_reset_hadamard_transport.py",
        "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py",
        "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
        "src/bhsm/interface/aether_full_reset_action_jacobian.py",
        "src/bhsm/interface/aether_full_sobolev_hybrid_actualization_v15_57.py",
        "src/bhsm/interface/aether_hybrid_standard_model_bundle_v15_53.py",
        "src/bhsm/interface/aether_n3_zero_background_calderon_closure_v17_97.py",
        "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
        str(MODULE.relative_to(ROOT)).replace("\\", "/"),
        str(SCRIPT.relative_to(ROOT)).replace("\\", "/"),
        str(THEORY.relative_to(ROOT)).replace("\\", "/"),
        str(TEST.relative_to(ROOT)).replace("\\", "/"),
    )
    hashes = {
        source: _sha256(ROOT / source)
        for source in sorted(source_paths)
        if (ROOT / source).is_file()
    }
    validation = {
        "boundary_phase_space_separates_canonical_and_null_directions": (
            phase["gauge"]["finite_witness_rank"] > 0
            and phase["fermion"]["finite_witness_rank"] > 0
            and phase["HS"]["finite_witness_rank"] == 0
        ),
        "no_HS_canonical_partner_manufactured": not phase["HS"][
            "forced_canonical_partner_added"
        ],
        "all_candidate_reset_sources_classified": len(sources) == 9,
        "nonzero_gauge_connection_trace_map_absent": (
            reset["gauge"]["status"] == "MISSING"
            and reset["first_missing_component"] == EXACT_MISSING_DATUM
        ),
        "fermion_map_remains_exact": reset["fermion"]["status"] == "DEFINED",
        "reference_maps_are_exact_symplectic": (
            reference["zero_field_gauge_identity"]["symplectic_residual"]
            < 1.0e-12
            and reference["AE2_fermion_cotangent_lift"][
                "symplectic_residual"
            ]
            < 1.0e-12
            and reference["zero_field_gauge_identity"][
                "canonical_one_form_residual"
            ]
            < 1.0e-12
        ),
        "constant_zero_background_reset_rejected": (
            reference["v15_57_constant_reconstruction"]["symplectic_residual"]
            > 0.0
            and not reference["v15_57_constant_reconstruction"][
                "may_be_used_as_nonzero_GFHS_reset"
            ]
        ),
        "full_canonicality_fails_closed_as_incomplete": (
            canonicality["reset_is_incompletely_defined"]
            and not canonicality["full_canonicality_testable"]
            and canonicality["Delta_omega_full"] is None
            and not canonicality["reset_is_proven_nonsymplectic"]
        ),
        "exactness_not_tested_without_map": (
            exactness["beta_nonzero_GFHS"] is None
            and exactness["d_beta_nonzero_GFHS"] is None
            and not exactness["S_RESET_GFHS_derived"]
        ),
        "BRST_and_adjoint_maps_not_independently_parameterized": (
            not brst["independent_ghost_coefficient_added"]
            and not brst["independent_antighost_coefficient_added"]
            and not brst["nonzero_BRST_reset_instantiable"]
        ),
        "HS_nullity_not_misreported_as_graph_selection": (
            hs["normal_Legendre_rank"] == 0
            and not hs["HS_graph_derivatives_may_be_declared_structural_zero"]
        ),
        "graph_jets_and_global_S2_S4_not_fabricated": (
            graph["D_Theta_at_zero"] is None
            and graph["D2_Theta_at_zero"] is None
            and graph["D3_Theta_at_zero"] is None
            and graph["S2_global"] == "BLOCKED"
            and graph["S4_global"] == "BLOCKED"
        ),
        "event_balance_not_fabricated": (
            balance["total"] is None
            and not balance["global_residual_evaluable"]
            and not balance["empirical_repair_added"]
        ),
        "child_inheritance_reuses_fermion_fibers": (
            not inheritance["nine_frozen_family_mode_fibers_rebuilt"]
            and not inheritance["full_field_child_inheritance_promoted"]
        ),
        "one_exact_open_datum": claims["exact_missing_datum"]
        == EXACT_MISSING_DATUM,
        "Gate7_and_physical_flags_preserved": (
            not claims["FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND"]
            and not claims["physical_background_bound"]
            and not claims["physical_HS_direction_derived"]
            and not claims["physical_yukawas_derived"]
            and not claims["physical_spectrum_derived"]
            and not claims["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_RESET_BOUNDARY_GENERATING_FUNCTIONAL_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "reset_classification": "INCOMPLETELY_DEFINED",
        "prior_blocker_refinement": {
            "prior_missing_variational_datum": (
                "ACTION_OWNED_BRST_COMPATIBLE_MIXED_RESET_BOUNDARY_"
                "VARIATION_D_PhiSM_D_GAMMA0_SQUARED_"
                "S_RESET_GFHS[B;0,0]"
            ),
            "refined_first_obstruction": EXACT_MISSING_DATUM,
            "relation": (
                "THE_MIXED_VARIATION_CANNOT_BE_FORMED_BECAUSE_THE_NONZERO_"
                "GAUGE_CONNECTION_TRACE_COMPONENT_OF_R_B_IS_UNDEFINED"
            ),
        },
        "boundary_phase_space": phase,
        "existing_source_search": sources,
        "actual_reset_map": reset,
        "reference_canonicality": reference,
        "Delta_omega": canonicality,
        "beta_and_exactness": exactness,
        "S_RESET_GFHS": {
            "derived": False,
            "zero_field_normalization": 0.0,
            "nonzero_functional": None,
            "blocked_by": EXACT_MISSING_DATUM,
        },
        "BRST_compatibility": brst,
        "HS_rank_zero_handling": hs,
        "graph_generation": graph,
        "global_action_derivatives": {
            "S1_global": graph["S1_global"],
            "S2_global": graph["S2_global"],
            "S3_global": graph["S3_global"],
            "S4_global": graph["S4_global"],
        },
        "event_Noether_Hamiltonian_balance": balance,
        "AE4_child_inheritance": inheritance,
        "empirical_inputs": [],
        "VALIDATED": [
            "ACTION_OWNED_BOUNDARY_PHASE_SPACE_WITH_EXPLICIT_HS_NULL_SECTOR",
            "REFERENCE_GAUGE_IDENTITY_AND_AE2_FERMION_LIFT_ARE_EXACT_SYMPLECTIC",
            "GHOST_AND_ANTIGHOST_RESET_RULES_ARE_INDUCED_NOT_INDEPENDENT",
            "ZERO_FIELD_RESET_GENERATOR_NORMALIZES_TO_ZERO",
            "NINE_FROZEN_FAMILY_MODE_FIBERS_REMAIN_UNCHANGED",
        ],
        "INVALIDATED": [
            "V15_57_CONSTANT_RECONSTRUCTION_IS_A_NONZERO_GFHS_CANONICAL_RESET",
            "RETURNED_SM_BUNDLE_ISOMORPHISM_CLASS_TRANSPORTS_CONNECTION_ONE_FORMS",
            "V17_97_ORIGIN_MATCH_DEFINES_THE_NONZERO_CALDERON_GRAPH",
            "AE4_RETARDED_ASSEMBLER_GENERATES_ITS_OWN_SECTOR_RESET_MAPS",
            "HS_PRESYMPLECTIC_NULLITY_SELECTS_ALL_HS_GRAPH_JETS_TO_ZERO",
        ],
        "OPEN": [EXACT_MISSING_DATUM],
        "EXACT_NEXT_OBJECT": EXACT_MISSING_DATUM,
        "exact_next_calculation": (
            "DERIVE_FROM_THE_ACTION_OWNED_EVENT_ATTACHMENT_INCIDENCE_THE_"
            "NONZERO_GAUGE_CONNECTION_TRACE_MAP_GAMMA0_A_CHILD=R_A[B;"
            "GAMMA0_A_EVENT];_THEN_TEST_ITS_MAXWELL_CONORMAL_COTANGENT_LIFT_"
            "AND_ONLY_IF_SYMPLECTIC_FORM_R_A_PULLBACK_ALPHA_MINUS_ALPHA"
        ),
        "physical_background_bound": False,
        "physical_HS_direction_derived": False,
        "physical_yukawas_derived": False,
        "physical_spectrum_derived": False,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "FULL_BHSM_COMPLETE": False,
        "claims": claims,
        "source_sha256": hashes,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
