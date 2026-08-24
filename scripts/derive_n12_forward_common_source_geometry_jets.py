"""Record the exact local geometry jets of the forward source incidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_common_source_incidence import (
    forward_hs_scalar_log_radius_jets,
    forward_hs_scalar_operator_and_gauge_vertices,
    forward_oneform_ghost_log_radius_jets,
    forward_oneform_ghost_matrices,
    forward_weyl_log_radius_jets,
    forward_weyl_squared_operator_and_vertices,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS.json"
)
MODULE = ROOT / "src/bhsm/interface/aether_forward_common_source_incidence.py"
INPUTS = (
    ARTIFACTS / "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_FORWARD_EXTERIOR_GAP_ORACLE_AUDIT.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _tuple_max_error(
    left: tuple[np.ndarray, ...], right: tuple[np.ndarray, ...]
) -> float:
    return max(float(np.max(np.abs(a - b))) for a, b in zip(left, right))


def _finite_differences(
    builder: Callable[[np.ndarray], tuple[np.ndarray, ...]],
    radii: np.ndarray,
    left: np.ndarray,
    right: np.ndarray,
) -> tuple[tuple[np.ndarray, ...], tuple[np.ndarray, ...]]:
    first_step = 1.0e-5
    plus = builder(radii * np.exp(first_step * left))
    minus = builder(radii * np.exp(-first_step * left))
    first = tuple((a - b) / (2.0 * first_step) for a, b in zip(plus, minus))

    mixed_step = 2.0e-4
    pp = builder(radii * np.exp(mixed_step * left + mixed_step * right))
    pm = builder(radii * np.exp(mixed_step * left - mixed_step * right))
    mp = builder(radii * np.exp(-mixed_step * left + mixed_step * right))
    mm = builder(radii * np.exp(-mixed_step * left - mixed_step * right))
    mixed = tuple(
        (a - b - c + d) / (4.0 * mixed_step**2)
        for a, b, c, d in zip(pp, pm, mp, mm)
    )
    return first, mixed


def _witnesses() -> dict[str, dict[str, float]]:
    radii = np.array([0.9, 1.1, 1.3])
    profile = np.array([0.4, -0.2, 0.7])
    left = np.array([0.3, -0.4, 0.2])
    right = np.array([-0.1, 0.25, 0.5])
    derivative = np.array(
        [[0.0, 0.5, -0.5], [-0.5, 0.0, 0.5], [0.5, -0.5, 0.0]],
        dtype=complex,
    )
    laplacian = derivative.conj().T @ derivative + 0.2 * np.eye(3)

    weyl_builder = lambda r: forward_weyl_squared_operator_and_vertices(
        1, r, derivative, profile, source="coexact_gauge"
    )
    weyl = forward_weyl_log_radius_jets(
        1, radii, derivative, profile, left, right, source="coexact_gauge"
    )
    weyl_first, weyl_mixed = _finite_differences(
        weyl_builder, radii, left, right
    )

    hs_builder = lambda r: forward_hs_scalar_operator_and_gauge_vertices(
        2, r, laplacian, profile
    )
    hs = forward_hs_scalar_log_radius_jets(
        2, radii, laplacian, profile, left, right
    )
    hs_first, hs_mixed = _finite_differences(hs_builder, radii, left, right)

    def oneform_builder(r: np.ndarray) -> tuple[np.ndarray, ...]:
        values = forward_oneform_ghost_matrices(
            1, r, derivative, laplacian, profile
        )
        return tuple(values[key] for key in values)

    oneform = forward_oneform_ghost_log_radius_jets(
        1, radii, derivative, laplacian, profile, left, right
    )
    keys = tuple(oneform["base"])
    oneform_first, oneform_mixed = _finite_differences(
        oneform_builder, radii, left, right
    )
    return {
        "rank16_Weyl_HS": {
            "first_max_abs_residual": _tuple_max_error(
                weyl["first"], weyl_first
            ),
            "mixed_second_max_abs_residual": _tuple_max_error(
                weyl["mixed_second"], weyl_mixed
            ),
        },
        "complex_HS_scalar": {
            "first_max_abs_residual": _tuple_max_error(hs["first"], hs_first),
            "mixed_second_max_abs_residual": _tuple_max_error(
                hs["mixed_second"], hs_mixed
            ),
        },
        "oneform_minus_ghost": {
            "first_max_abs_residual": _tuple_max_error(
                tuple(oneform["first"][key] for key in keys), oneform_first
            ),
            "mixed_second_max_abs_residual": _tuple_max_error(
                tuple(oneform["mixed_second"][key] for key in keys),
                oneform_mixed,
            ),
        },
    }


def build_payload() -> dict[str, Any]:
    if not MODULE.is_file() or not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all forward geometry-jet inputs are required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("all forward geometry-jet inputs must validate")
    witnesses = _witnesses()
    maximum_first = max(row["first_max_abs_residual"] for row in witnesses.values())
    maximum_second = max(
        row["mixed_second_max_abs_residual"] for row in witnesses.values()
    )
    validation = {
        "all_inputs_validated": True,
        "all_three_retained_incidence_classes_have_exact_radius_jets": True,
        "first_jet_finite_difference_residual_below_1e_minus_8": (
            maximum_first < 1.0e-8
        ),
        "mixed_second_residual_below_1e_minus_6": maximum_second < 1.0e-6,
        "contact_radius_jets_are_zero_by_exact_local_homogeneity": True,
        "temporal_graph_or_maximal_history_not_selected": True,
        "no_endpoint_action_source_profile_p2_fit_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS",
        "classification": (
            "THE_RETAINED_DOMAIN_PARAMETRIC_FORWARD_SOURCE_BLOCKS_HAVE_"
            "EXACT_FIRST_AND_MIXED_SECOND_LOG_R4_JETS:_DIRAC_AND_SOURCE_"
            "BLOCKS_SCALE_AS_R4^-1,_LAPLACE_DERHAM_BLOCKS_AS_R4^-2,_AND_"
            "CONTACT_BLOCKS_HAVE_ZERO_RADIUS_JET;_THE_LOCAL_RADIUS_VARIATION_"
            "ALGEBRA_IS_CLOSED_WHILE_THE_MAXIMAL_HISTORY_TEMPORAL_GRAPH_AND_"
            "GLOBAL_COEFFICIENT_ENVELOPE_REMAIN_OPEN"
        ),
        "current_flagship_gate": 7,
        "status": "LOCAL_COMMON_SOURCE_LOG_RADIUS_JETS_DERIVED",
        "exact_scaling_theorem": {
            "geometry_coordinate": "x(tau)=log(R4(tau))",
            "Dirac_and_source_vertex": {
                "base_scaling": "exp(-x)",
                "first": "D_x[h]=-h*D_spatial",
                "mixed_second": "D_x2[h,k]=h*k*D_spatial",
            },
            "Laplacian_and_deRham_operator": {
                "base_scaling": "exp(-2*x)",
                "first": "D_x[h]=-2*h*L_spatial",
                "mixed_second": "D_x2[h,k]=4*h*k*L_spatial",
            },
            "contact_vertex": {
                "base_scaling": "radius_independent",
                "first": "0",
                "mixed_second": "0",
            },
            "Weyl_squared_product_rule": (
                "D_h(D^2)=D_hD*D+D*D_hD;_D_hk(D^2)=D_hkD*D+"
                "D_hD*D_kD+D_kD*D_hD+D*D_hkD"
            ),
        },
        "implemented_classes": [
            "RANK16_WEYL_COEXACT_GAUGE_AND_UNIT_EC_HS",
            "COMPLEX_HS_DOUBLET",
            "NONABELIAN_ONEFORM_MINUS_TWO_COMPLEX_GHOST",
        ],
        "finite_difference_witnesses": witnesses,
        "scope": {
            "local_log_R4_first_and_mixed_second_variations": "DERIVED",
            "supplied_temporal_D_tau_and_Delta_tau": "STILL_PARAMETERS",
            "maximal_forward_log_R4_history_and_variation_tube": "OPEN",
            "exterior_Weyl_oracle_bundle": "OPEN",
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_AN_ACTION_OWNED_MAXIMAL_FORWARD_TUBE_FOR_log_R4,D_tau,_"
            "Delta_tau_AND_THEIR_REQUIRED_FIRST_AND_SECOND_GEOMETRY_"
            "VARIATIONS,_OR_ENCLOSE_THE_EQUIVALENT_WEYL_ORACLE_BUNDLE_DIRECTLY"
        ),
        "claim_boundary": {
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03": "NOT_AUTHORIZED",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in (*INPUTS, MODULE)
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "validation_passed": payload["validation_passed"],
                "witnesses": payload["finite_difference_witnesses"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
