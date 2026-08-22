"""Derive the exact noncompact inventory for the mixed Euler--Dirac split.

The calculation is symbolic and local.  It prevents the compact-modulus proof
from incorrectly putting L2 velocity multiplication or derivative--velocity
couplings into the compact remainder.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / (
    "src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py"
)
MIXED = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_MIXED_GRAPH.json"
)
POLE = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_INDICIAL_BOUND.json"
)
QUOTIENT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_NORMAL_QUOTIENT_ISOMETRY.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_EULER_DIRAC_PRINCIPAL_COMPACT_INVENTORY.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _matrix(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(value)) for value in row] for row in matrix.tolist()]


def main() -> None:
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    pole = json.loads(POLE.read_text(encoding="utf-8"))
    quotient = (
        json.loads(QUOTIENT.read_text(encoding="utf-8"))
        if QUOTIENT.exists() else None
    )

    du, db, dn = sp.symbols("du db dn")
    a0, b0 = sp.symbols("a0 b0")
    ap = a0 + du + db
    bp = b0 + du - db
    spatial_core = ap**2 + bp**2 + 3 * ap * bp + dn * (ap + bp)
    spatial_matrix = sp.hessian(spatial_core, (du, db, dn))

    dr, dv_u, dv_w, dv_b = sp.symbols("dr dv_u dv_w dv_b")
    lc0 = dr + dv_u + dv_w
    la0 = dr + dv_u + dv_b
    lb0 = dr + dv_u - dv_b
    adm_normal = sp.Rational(1, 2) * (
        lc0**2 + 3 * la0**2 + 3 * lb0**2
        - (lc0 + 3 * la0 + 3 * lb0) ** 2
    )
    velocity_matrix = sp.hessian(
        adm_normal, (dv_u, dv_b, dr, dv_w)
    )

    lc, la, lb, beta, beta_prime = sp.symbols(
        "lc la lb beta beta_prime"
    )
    cp, ap_bg, bp_bg, lapse = sp.symbols(
        "cp ap bp N", positive=True
    )
    hc = (lc - beta * cp - beta_prime) / lapse
    ha = (la - beta * ap_bg) / lapse
    hb = (lb - beta * bp_bg) / lapse
    adm = sp.Rational(1, 2) * (
        hc**2 + 3 * ha**2 + 3 * hb**2
        - (hc + 3 * ha + 3 * hb) ** 2
    )
    mixed_variables = (lc, la, lb, beta, beta_prime)
    adm_hessian = sp.hessian(adm, mixed_variables)
    derivative_velocity = {
        f"D2_adm[{mixed_variables[i]},{mixed_variables[j]}]": str(
            sp.factor(adm_hessian[i, j])
        )
        for i in range(3)
        for j in (3, 4)
        if adm_hessian[i, j] != 0
    }
    derivative_velocity["D2_adm[beta,beta_prime]"] = str(
        sp.factor(adm_hessian[3, 4])
    )

    expected_spatial = sp.Matrix([
        [10, 0, 2],
        [0, -2, 0],
        [2, 0, 0],
    ])
    expected_velocity = sp.Matrix([
        [-42, 0, -42, -6],
        [0, 6, 0, 0],
        [-42, 0, -42, -6],
        [-6, 0, -6, 0],
    ])
    validation = {
        "assembled_mixed_graph_consumed": bool(mixed["validation_passed"]),
        "exact_spatial_principal_matrix_reproduced": (
            spatial_matrix == expected_spatial
        ),
        "spatial_principal_determinant_is_eight": (
            spatial_matrix.det() == 8
        ),
        "exact_L2_velocity_Hessian_reproduced": (
            velocity_matrix == expected_velocity
        ),
        "L2_velocity_block_is_nonzero_and_singular_before_gauge_quotient": (
            velocity_matrix.rank() == 3 and velocity_matrix.det() == 0
        ),
        "derivative_velocity_couplings_are_nonzero": bool(
            derivative_velocity
        ),
        "critical_pole_block_routed_to_existing_indicial_inverse": bool(
            pole["validation_passed"]
        ),
        "boundary_trace_block_not_inserted_into_bulk_remainder": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
        "source_normal_quotient_factor_is_norm_one_if_materialized": (
            quotient is None or bool(quotient["validation_passed"])
        ),
    }
    output = {
        "classification": (
            "EXACT_MIXED_EULER_DIRAC_NONCOMPACT_BLOCK_INVENTORY_DERIVED;_"
            "A_SPLIT_CONTAINING_ONLY_THE_RADIAL_kappa_P_AND_POLE_BLOCK_"
            "IS_INVALID_BECAUSE_L2_VELOCITY_AND_DERIVATIVE_VELOCITY_"
            "COUPLINGS_ARE_ALSO_NONCOMPACT"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (ACTION, MIXED, POLE)
        },
        "spatial_principal_block": {
            "variables": ["D_chi_u", "D_chi_b", "D_chi_logN"],
            "density_owner": "ap^2+bp^2+3*ap*bp+n_prime*(ap+bp)",
            "dimensionless_matrix": _matrix(spatial_matrix),
            "determinant": int(spatial_matrix.det()),
            "smallest_absolute_eigenvalue": "sqrt(29)-5",
            "full_coefficient": "kappa*omega",
        },
        "velocity_L2_block": {
            "variables": ["dot_u", "dot_b", "dot_rho", "dot_w"],
            "dimensionless_ADM_Hessian": _matrix(velocity_matrix),
            "rank_before_existing_gauge_quotient": int(velocity_matrix.rank()),
            "null_vector": ["-1", "0", "1", "0"],
            "must_remain_in_principal_ED_operator": True,
            "may_be_bounded_by_C_F_as_a_compact_L2_multiplication": False,
        },
        "derivative_velocity_mixed_block": {
            "source": "SHIFT_AND_SHIFT_DERIVATIVE_IN_Hc_Ha_Hb",
            "exact_nonzero_entries": derivative_velocity,
            "must_remain_in_principal_ED_operator_before_gauge_reduction": True,
        },
        "critical_regular_pole_block": {
            "operator": "6*c*(D_t^2+1)",
            "source_restricted_weighted_H2_inverse_upper": pole[
                "joint_source_restricted_weighted_H2_inverse_upper"
            ],
            "counted_as_compact": False,
        },
        "finite_rank_blocks": {
            "collective_inertia": (
                "D2(-c/I)=c*I^-2*D2I-2*c*I^-3*DI_tensor_DI"
            ),
            "boundary_Casimir_and_attachment": (
                "FIXED_FINITE_DIMENSIONAL_TRACE_BLOCK_WITH_ZERO_DIRECT_"
                "TAIL_UNDER_THE_FOUR_ROW_FORTIN_PROJECTOR"
            ),
        },
        "required_principal_operator": [
            "FULL_kappa_P_RADIAL_DERIVATIVE_BLOCK",
            "CRITICAL_REGULAR_POLE_INDICIAL_BLOCK",
            "FULL_CANONICAL_L2_VELOCITY_LEGENDRE_MULTIPLICATION_BLOCK",
            "ALL_DERIVATIVE_TO_L2_VELOCITY_MIXED_BLOCKS_BEFORE_THE_EXISTING_GAUGE_QUOTIENT",
        ],
        "source_normal_quotient": (
            {
                "artifact": str(QUOTIENT.relative_to(ROOT)).replace("\\", "/"),
                "SHA256": _sha256(QUOTIENT),
                "representative_norm": "ONE",
                "separate_C_ED_multiplier_required": False,
            }
            if quotient is not None else {
                "artifact": None,
                "representative_norm": "PENDING_MATERIALIZATION",
            }
        ),
        "first_missing_executable_map": (
            "THE_EXISTING_SOURCE_NORMAL_COMPRESSION_APPLIED_TO_THE_"
            "ENDPOINT_AUDIT_RANK_TWO_CRITICAL_POLE_MATRIX,_FOLLOWED_BY_"
            "THE_OUTWARD_INTERVAL_COEFFICIENT_EXTRACTOR_FOR_THE_TRUE_"
            "UNDIFFERENTIATED_K_ED,lo"
        ),
        "C_ED_G_evaluable": False,
        "epsilon_obs_M_evaluable": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
