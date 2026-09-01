"""Materialize the same-C2 continuous-frequency gauge/ghost Hessian."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_c2_lorentzian_gauge_ghost_hessian import (
    ACTION_VERSION,
    CLASSIFICATION,
    constraint_ghost_frequency_block,
    current_c2_transverse_frequency_symbol,
    gauge_ghost_hessian_claim_boundary,
    lowest_transverse_residue_witness,
)


ARTIFACTS = ROOT / "artifacts"
DESCRIPTOR_JSON = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
)
DESCRIPTOR_NPZ = ARTIFACTS / (
    "flagship_integration/BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.npz"
)
TARGET = ARTIFACTS / (
    "action_extension/BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json"
)
INPUTS = (
    DESCRIPTOR_JSON,
    DESCRIPTOR_NPZ,
    ARTIFACTS / "action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",
    ARTIFACTS / "action_extension/BHSM_AE3_C2_COEXACT_GAUGE_FORM_SHAPE.json",
    ARTIFACTS / "BHSM_aether_event_weighted_unified_pushforward_v15_71.json",
    ARTIFACTS / "BHSM_aether_einstein_cartan_joint_pushforward_v15_75.json",
    ARTIFACTS / "BHSM_aether_m5_m4_gauge_higgs_ownership_v15_60.json",
    ARTIFACTS / "BHSM_aether_nonabelian_coexact_vertex_v16_03.json",
    ARTIFACTS / "BHSM_aether_nonabelian_derham_response_v16_04.json",
    ROOT / "src/bhsm/interface/ae3_c2_lorentzian_gauge_ghost_hessian.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _summary(values: np.ndarray) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "minimum": float(np.min(array)),
        "maximum": float(np.max(array)),
        "maximum_absolute": float(np.max(np.abs(array))),
    }


def _complex_matrix(matrix: np.ndarray) -> dict[str, list[list[float]]]:
    value = np.asarray(matrix, dtype=complex)
    return {
        "real": value.real.tolist(),
        "imaginary": value.imag.tolist(),
    }


def build_payload() -> dict[str, Any]:
    missing = [path.as_posix() for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("gauge/ghost Hessian inputs required: " + ", ".join(missing))
    descriptor = _load(DESCRIPTOR_JSON)
    ae3 = _load(INPUTS[2])
    form = _load(INPUTS[3])
    weighted = _load(INPUTS[4])
    parent = _load(INPUTS[5])
    no_go = _load(INPUTS[6])
    coexact = _load(INPUTS[7])
    derham = _load(INPUTS[8])
    with np.load(DESCRIPTOR_NPZ) as data:
        log_radii = np.asarray(data["node_log_R4_center"], dtype=float)
    residue = lowest_transverse_residue_witness()
    zero_symbol = current_c2_transverse_frequency_symbol(
        log_radii=log_radii, omega=0.0
    )
    probe_symbol = current_c2_transverse_frequency_symbol(
        log_radii=log_radii, omega=0.125
    )
    constraint = constraint_ghost_frequency_block(
        omega=0.375,
        scalar_laplacian=3.0,
        z_temporal=float(residue["electric_weight_integral"]),
        z_spatial=float(residue["static_dimensionless_DtN"]) / 4.0,
    )
    static_identity_residual = abs(
        float(residue["static_dimensionless_DtN"])
        - float(residue["static_energy_identity_right_hand_side"])
    )
    frequency_derivative_residual = abs(
        float(residue["d_DtN_d_q_squared_at_zero"])
        - float(residue["centered_difference_derivative"])
    )
    ghost_residual = abs(
        constraint["ghost_Faddeev_Popov_symbol"]
        - constraint["expected_ghost_symbol"]
    )
    localization = weighted["unified_localization_contract"]
    smooth = no_go["smooth_gauge_pushforward"]
    validation = {
        "same_AE3_action_owner": ae3["action_version"] == ACTION_VERSION,
        "actual_reset_generated_C2_descriptor_valid": descriptor["validation_passed"] is True,
        "retained_birth_trace_preserved": descriptor["endpoint_event_child_partition"][
            "retained_boundary"
        ] == "C2_BIRTH_TRACE_NODE_0",
        "continuous_frequency_not_cycle_surrogate": zero_symbol["frequency_domain"]
        == "CONTINUOUS_REAL_OMEGA__NOT_PERIODIC_CYCLE_MODE",
        "parent_Maxwell_coefficient_relation_owned": parent["first_order_parent_action"][
            "coefficient_relation"
        ] == "K_F5/K_G5=RF^2/2",
        "AE3_weight_inserted_before_derivatives": localization["placement"]
        == "before_gauge_and_fermion_source_derivatives",
        "v16_03_coexact_BRST_machinery_reused": coexact["claim_boundary"][
            "exact_coexact_curl_blocks_assembled"
        ]
        is True,
        "v16_04_periodic_response_not_promoted": derham["claim_boundary"][
            "angular_heat_tail_converged"
        ]
        is False,
        "current_C2_form_predecessor_valid": form["validation_passed"] is True,
        "static_DtN_energy_identity": static_identity_residual < 2.0e-10,
        "continuous_frequency_derivative_matches_envelope_integral": frequency_derivative_residual
        < 2.0e-8,
        "constraint_Maxwell_Ward_identity": constraint["Maxwell_Ward_residual"]
        < 1.0e-12,
        "ghost_is_same_gauge_functional_derivative": ghost_residual < 1.0e-12,
        "BRST_degree_weights_close": constraint["BRST_real_degree_weights"]
        == {"temporal_plus_longitudinal_bosons": 2, "complex_ghost": -2},
        "smooth_bulk_weight_no_go_retained": smooth[
            "smooth_bulk_profile_closes_Lorentz_invariant_M4_Maxwell_term"
        ]
        is False,
        "temporal_spatial_residue_mismatch_is_strict": 0.0
        < float(residue["temporal_to_complete_spatial_mode_residue_ratio"])
        < 1.0,
        "mismatch_not_renormalized": gauge_ghost_hessian_claim_boundary()[
            "residue_outcome"
        ]
        == "MISMATCH_RECORDED__NOT_RENORMALIZED",
        "no_independent_continuous_coefficient": not probe_symbol[
            "independent_residue_inserted"
        ],
        "photon_not_promoted": not gauge_ghost_hessian_claim_boundary()[
            "physical_photon_derived"
        ],
    }
    return {
        "artifact": "BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "domain": {
            "background": "ACTUAL_RESET_GENERATED_C2_PROOF_CENTER_HISTORY",
            "retained_boundary": "C2_BIRTH_TRACE_NODE_0",
            "far_core_role": "NOT_USED_BY_THE_LOCAL_CONTINUOUS_FREQUENCY_SYMBOL",
            "radial_domain": "SMOOTH_AE3_WEIGHTED_HALF_CAP_TRACE_TO_SIGMA_ZERO_WALL",
            "frequency_domain": "CONTINUOUS_REAL_OMEGA_NEAR_ZERO",
            "periodic_cycle_frequency_used": False,
        },
        "parent_action": {
            "quadratic_term": "(K_F5/4)*integral_M5*W*Tr_16(F_MN*F^MN)",
            "weight": "W=(1-4*sigma^2)*(1+X_eta^3)",
            "coefficient_relation": "K_F5/K_G5=RF^2/2",
            "new_ZA_g_gprime_alpha_metric_cone_or_residue": None,
        },
        "continuous_frequency_transverse_DtN": residue,
        "current_C2_symbol": {
            "segment_count": zero_symbol["segment_count"],
            "boundary_radius_summary": _summary(zero_symbol["boundary_radius"]),
            "coexact_eigenvalue_summary": _summary(zero_symbol["coexact_eigenvalue"]),
            "Z_t_over_K_F5_summary": _summary(zero_symbol["Z_t_over_K_F5"]),
            "Z_s_over_K_F5_summary": _summary(zero_symbol["Z_s_over_K_F5"]),
            "residue_ratio_summary": _summary(zero_symbol["residue_ratio"]),
            "omega_probe": probe_symbol["frequency_parameter"],
            "H_probe_over_K_F5_summary": _summary(
                probe_symbol["H_transverse_low_frequency_over_K_F5"]
            ),
            "formula": zero_symbol["formula"],
        },
        "constraint_and_ghost_witness": {
            "basis": list(constraint["basis"]),
            "omega": 0.375,
            "scalar_laplacian": 3.0,
            "Maxwell_constraint_block": _complex_matrix(
                constraint["Maxwell_constraint_block"]
            ),
            "gauge_fixing_block_xi_one": _complex_matrix(
                constraint["gauge_fixing_block_xi_one"]
            ),
            "gauge_fixed_block": _complex_matrix(constraint["gauge_fixed_block"]),
            "Maxwell_Ward_residual": constraint["Maxwell_Ward_residual"],
            "ghost_Faddeev_Popov_symbol": constraint[
                "ghost_Faddeev_Popov_symbol"
            ].real,
            "BRST_real_degree_weights": constraint["BRST_real_degree_weights"],
            "physical_transverse_residue_changed_by_gauge_fixing": constraint[
                "physical_transverse_residue_changed_by_gauge_fixing"
            ],
        },
        "decision": {
            "question": "DOES_THE_COMPLETE_ACTION_DERIVED_REDUCTION_PRODUCE_ONE_CONSISTENT_PHYSICAL_GAUGE_RESIDUE",
            "answer": "NO_ON_THE_CURRENT_SMOOTH_PARENT_TRACE_DOMAIN",
            "Z_t_equals_Z_s": False,
            "mismatch_not_renormalized": True,
            "responsible_action_domain_terms": [
                "electric_weight_W*RF*r",
                "magnetic_weight_W*RF/r",
                "positive_radial_gradient_DtN_energy",
                "smooth_regular_bulk_trace_domain_with_r_strictly_less_than_r_boundary_in_the_interior",
            ],
        },
        "claim_boundary": gauge_ghost_hessian_claim_boundary(),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "CURRENT_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN_DERIVED": True,
        "CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED": False,
        "CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise SystemExit("C2 Lorentzian gauge/ghost Hessian failed: " + ", ".join(failed))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    main()
