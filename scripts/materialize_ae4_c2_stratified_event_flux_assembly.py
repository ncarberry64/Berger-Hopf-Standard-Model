"""Materialize the AE4 current-C2 stratified event-flux assembly."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    ACTION_VERSION,
    CLASSIFICATION,
    SECTOR_ORDER,
    assemble_stratified_direct_sum,
    assembly_contract,
    canonical_noether_flux_balance,
    claim_boundary,
    solve_retarded_event_kkt,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY.json"
INPUTS = (
    A / "BHSM_AE4_STRATIFIED_DIRAC_ZETA_INDUCED_OWNER.json",
    A / "BHSM_AE4_EXISTING_ASSET_SYSTEM_INTEGRATION.json",
    A / "BHSM_AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN.json",
    A / "BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",
    A / "BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json",
    A / "BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",
    A / "BHSM_AE3_C2_HS_FERMION_MIXED_VARIATION.json",
    ROOT / "artifacts/n12_continuum_majorant_effectiveness/BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json",
    A / "BHSM_AE4_CURRENT_C2_STOP_GAUGE_BRST_CALDERON.json",
    A / "BHSM_AE4_CURRENT_C2_AFFINE72_GAUGE_CALDERON_FIRST_JET.json",
    A / "BHSM_AE4_CURRENT_C2_AFFINE72_PARTICLE_FIBER_CALDERON.json",
    A / "BHSM_AE4_CURRENT_C2_NONLINEAR_CARRIER_AUTHORITY_ADJUDICATION.json",
    ROOT / "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def theorem_witness() -> dict[str, Any]:
    sectors: OrderedDict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = OrderedDict()
    for index, sector in enumerate(SECTOR_ORDER):
        parent = np.asarray(((1.7 + 0.13 * index,),), dtype=complex)
        coupling = np.asarray(((0.17 + 0.01j * (index + 1),),), dtype=complex)
        child = np.asarray(((1.3 + 0.09 * index + 0.21j,),), dtype=complex)
        sectors[sector] = (parent, coupling, child)
    direct_sum = assemble_stratified_direct_sum(sectors)
    response = np.asarray(
        (
            (1.0, 0.0, 0.0, 0.0, 0.0, -0.35),
            (0.0, 0.0, 0.0, 0.0, 0.6, 1.0),
        ),
        dtype=complex,
    )
    source = np.asarray((0.11, -0.07, 0.04j, -0.03j, 0.16, -0.09), dtype=complex)
    target = np.asarray((0.08, -0.04), dtype=complex)
    solution = solve_retarded_event_kkt(
        parent_block=direct_sum["parent_block"],
        parent_child_coupling=direct_sum["parent_child_coupling"],
        child_retarded_block=direct_sum["child_retarded_block"],
        response_operator=response,
        source=source,
        response_target=target,
    )
    noether = canonical_noether_flux_balance(
        trace=solution["parent_trace"],
        event_tractions=solution["event_tractions"],
        generator=1.0j * np.eye(len(SECTOR_ORDER)),
    )
    return {"direct_sum": direct_sum, "solution": solution, "noether": noether}


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    json_sources = [_load(path) for path in INPUTS[:-1]]
    witness = theorem_witness()
    solution = witness["solution"]
    noether = witness["noether"]
    boundary = claim_boundary()
    gauge_brst = json_sources[-4]
    gauge_first_jet = json_sources[-3]
    particle_fiber = json_sources[-2]
    nonlinear_authority = json_sources[-1]
    validation = {
        "all_source_artifacts_validated": all(row["validation_passed"] for row in json_sources),
        "six_required_sectors_explicit": witness["direct_sum"]["all_required_sectors_explicit"],
        "nonzero_source_exercised": solution["nonzero_source_present"],
        "nonzero_response_target_exercised": solution["nonzero_response_target_present"],
        "event_flux_balance_exact": solution["event_canonical_flux_balance_norm"] < 2.0e-14,
        "future_child_equation_exact": solution["future_child_equation_residual_norm"] < 2.0e-14,
        "response_constraint_exact": solution["response_constraint_residual_norm"] < 2.0e-14,
        "retarded_passivity_identity_exact": solution["retarded_passivity_identity_residual"] < 2.0e-14,
        "retarded_child_and_parent_passive": (
            solution["child_imaginary_part_positive_semidefinite"]
            and solution["effective_imaginary_part_positive_semidefinite"]
        ),
        "noether_contraction_exact": abs(noether["canonical_noether_flux_residual"]) < 2.0e-14,
        "canonical_stop_gauge_BRST_center_block_attached": (
            gauge_brst["claim_boundary"][
                "AE4_CURRENT_C2_CANONICAL_STOP_COEXACT_CALDERON_CENTER_EVALUATED"
            ]
            and gauge_brst["claim_boundary"][
                "AE4_CURRENT_C2_CANONICAL_STOP_BRST_QUOTIENT_CENTER_EVALUATED"
            ]
            and gauge_brst["validation_passed"]
        ),
        "affine72_gauge_BRST_first_jet_candidate_attached_fail_closed": (
            gauge_first_jet["validation_passed"]
            and gauge_first_jet["claim_boundary"][
                "AE4_CURRENT_C2_AFFINE72_PROPER_TIME_GAUGE_CALDERON_FIRST_JET_EVALUATED"
            ]
            and not gauge_first_jet["carrier"]["nonlinear_exact_family_authority"]
        ),
        "affine72_particle_fiber_Calderon_candidate_attached_fail_closed": (
            particle_fiber["validation_passed"]
            and particle_fiber["claim_boundary"][
                "ALL_NINE_EXISTING_CHARGED_PARTICLE_FIBERS_ATTACHED_TO_CARRIER"
            ]
            and particle_fiber["scientific_result"]["attached_existing_fiber_count"]
            == 9
            and not particle_fiber["carrier"]["nonlinear_exact_family_authority"]
            and not particle_fiber["claim_boundary"][
                "CURRENT_C2_PHYSICAL_MASS_OPERATOR_DERIVED"
            ]
        ),
        "nonlinear_authority_obstruction_attached_without_physical_overclaim": (
            nonlinear_authority["validation_passed"]
            and nonlinear_authority["claim_boundary"][
                "G7_SINGLE_RADIUS_74D_CONTRACTION_ROUTE_OBSTRUCTED"
            ]
            and not nonlinear_authority["claim_boundary"][
                "G7_ROOT_NONEXISTENCE_DERIVED"
            ]
            and not nonlinear_authority["claim_boundary"][
                "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED"
            ]
        ),
        "physical_sector_values_not_overclaimed": not boundary[
            "AE4_CURRENT_C2_NONZERO_SECTOR_CALDERON_BLOCKS_EVALUATED"
        ],
        "encapsulation_not_overclaimed": not boundary["PHYSICAL_ENCAPSULATION_IDENTIFIED"],
    }
    return _canonical(
        {
            "artifact": "BHSM_AE4_C2_STRATIFIED_EVENT_FLUX_ASSEMBLY",
            "action_version": ACTION_VERSION,
            "classification": CLASSIFICATION,
            "assembly_contract": assembly_contract(),
            "evaluated_sector_attachment": {
                "sector": "gauge_transverse+gauge_constraint+BRST_ghost",
                "domain": "CANONICAL_STOP_CENTER_FRIEDRICHS",
                "coexact_boundary_value": gauge_brst["scientific_result"][
                    "midpoint_refinement_4"
                ]["coexact_Weyl_birth_value"],
                "BRST_cancellation_residual": gauge_brst["scientific_result"][
                    "midpoint_refinement_4"
                ]["BRST_cancellation_residual_norm"],
                "affine72_first_jet_candidate_2_norm": gauge_first_jet[
                    "scientific_result"
                ]["coexact_first_jet_2_norm"],
                "affine72_first_jet_moving_duration_to_radius_norm_ratio": (
                    gauge_first_jet["scientific_result"][
                        "moving_duration_to_log_radius_norm_ratio"
                    ]
                ),
                "affine72_first_jet_nonlinear_authority": False,
                "inserted_in_finite_theorem_witness": False,
                "why_not_inserted": (
                    "THE_GEOMETRY_ETA_SIGMA_AND_INTERACTING_FERMION_HS_BLOCKS_"
                    "PLUS_THE_OUTWARD_NONLINEAR_STOP_FAMILY_ARE_NOT_YET_CLOSED"
                ),
            },
            "evaluated_particle_fiber_attachment": {
                "sector": "fermion_family",
                "domain": "CANONICAL_STOP_CENTER_FRIEDRICHS",
                "existing_fiber_count": particle_fiber["scientific_result"][
                    "attached_existing_fiber_count"
                ],
                "spatial_channel": particle_fiber["carrier"]["spatial_channel"],
                "plus_chirality_Weyl_birth_value": particle_fiber[
                    "scientific_result"
                ]["plus_chirality_Weyl_birth_value"],
                "minus_chirality_Weyl_birth_value": particle_fiber[
                    "scientific_result"
                ]["minus_chirality_Weyl_birth_value"],
                "plus_chirality_affine72_first_jet_2_norm": particle_fiber[
                    "scientific_result"
                ]["plus_chirality_first_jet_2_norm"],
                "minus_chirality_affine72_first_jet_2_norm": particle_fiber[
                    "scientific_result"
                ]["minus_chirality_first_jet_2_norm"],
                "internal_Berger_labels_used_as_spatial_levels": False,
                "physical_mass_or_pole_extracted": False,
                "affine72_first_jet_nonlinear_authority": False,
                "inserted_in_finite_theorem_witness": False,
                "why_not_inserted": (
                    "THE_NONLINEAR_STOP_FAMILY_AND_INTERACTING_HS_MIXED_"
                    "FERMION_BLOCK_ARE_NOT_YET_CLOSED"
                ),
            },
            "nonlinear_carrier_authority_adjudication": {
                "single_radius_74D_contraction_route": "OBSTRUCTED",
                "root_nonexistence": "NOT_DERIVED",
                "physical_spacetime_instability": "NOT_DERIVED",
                "new_center_or_trajectory": "NOT_AUTHORIZED",
                "current_affine_operator_jets_have_nonlinear_authority": False,
                "exact_next_proof_object": nonlinear_authority[
                    "exact_next_calculation"
                ],
            },
            "finite_theorem_witness": witness,
            "claim_boundary": boundary,
            "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
            "validation": validation,
            "validation_passed": all(validation.values()),
            "FULL_BHSM_COMPLETE": False,
        }
    )


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE4 stratified event-flux assembly failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
