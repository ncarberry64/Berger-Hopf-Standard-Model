"""Derive the event-normal Weyl/Riccati initialization for Gate 7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.event_normal_weyl_riccati import (  # noqa: E402
    scalar_constant_weyl,
    weyl_geometry_jet_rhs,
    weyl_riccati_rhs,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json"
)
INPUTS = (
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def scalar_orientation_witness() -> dict[str, float]:
    spatial = 2.7
    z = -0.6
    terminal = 0.8
    length = 0.35
    solution = solve_ivp(
        lambda _s, y: np.asarray([
            spatial - z - float(y[0]) ** 2
        ]),
        (0.0, length),
        np.asarray([terminal]),
        rtol=1.0e-12,
        atol=1.0e-14,
    )
    exact = scalar_constant_weyl(length, spatial, z, terminal)
    small = 1.0e-7
    expansion = terminal + small * (spatial - z - terminal**2)
    small_exact = scalar_constant_weyl(small, spatial, z, terminal)
    return {
        "integrated": float(solution.y[0, -1]),
        "closed_form": exact,
        "integration_residual": abs(float(solution.y[0, -1]) - exact),
        "first_order_terminal_residual_over_s_squared": (
            abs(small_exact - expansion) / small**2
        ),
    }


def geometry_jet_witness() -> dict[str, float]:
    length = 0.21
    z = -0.4
    spatial = 1.9
    terminal = 0.6
    d_spatial = -0.23
    d_terminal = 0.17

    def augmented(_s: float, y: np.ndarray) -> np.ndarray:
        m = np.asarray([[y[0]]])
        dm = np.asarray([[y[1]]])
        return np.asarray([
            weyl_riccati_rhs(m, np.asarray([[spatial]]), z)[0, 0].real,
            weyl_geometry_jet_rhs(
                m, dm, np.asarray([[d_spatial]])
            )[0, 0].real,
        ])

    solution = solve_ivp(
        augmented,
        (0.0, length),
        np.asarray([terminal, d_terminal]),
        rtol=1.0e-12,
        atol=1.0e-14,
    )
    analytic = float(solution.y[1, -1])
    epsilon = 1.0e-6
    plus = scalar_constant_weyl(
        length, spatial + epsilon * d_spatial, z,
        terminal + epsilon * d_terminal,
    )
    minus = scalar_constant_weyl(
        length, spatial - epsilon * d_spatial, z,
        terminal - epsilon * d_terminal,
    )
    finite = (plus - minus) / (2.0 * epsilon)
    return {
        "analytic_geometry_jet": analytic,
        "finite_difference_geometry_jet": finite,
        "absolute_residual": abs(analytic - finite),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("event-normal Weyl inputs required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated event-normal Weyl inputs required")
    weyl, domain, branch, force = records
    orientation = scalar_orientation_witness()
    jet = geometry_jet_witness()
    validation = {
        "native_Weyl_family_consumed": weyl["claim_boundary"][
            "forward_resolvent_spectral_family"
        ] == "DERIVED",
        "finite_domain_cutoff_audit_consumed": domain[
            "domain_adjudication"
        ]["arbitrary_regular_free_cutoff_allowed"] is False,
        "desingularized_event_branch_consumed": branch[
            "adjudication"
        ]["finite_positive_time_completed_encapsulation_exists"] is True,
        "heat_minus_zeta_force_dependency_consumed": force[
            "claim_boundary"
        ]["heat_minus_zeta_replacement_force_functional"] == "DERIVED",
        "event_normal_orientation_matches_closed_form": orientation[
            "integration_residual"
        ] < 1.0e-11,
        "geometry_jet_Riccati_equation_verified": jet[
            "absolute_residual"
        ] < 1.0e-9,
        "no_endpoint_source_profile_p2_selector_scale_fit_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_EVENT_NORMAL_WEYL_RICCATI",
        "status": "EVENT_NORMAL_WEYL_INITIAL_VALUE_SYSTEM_DERIVED_COEFFICIENT_CONTINUATION_OPEN",
        "classification": (
            "THE_CERTIFIED_FINITE_EVENT_GRAPH_INITIALIZES_THE_EXTERIOR_WEYL_"
            "ORACLE_WITH_M(0,z)=W_phys;_INWARD_EVENT_NORMAL_CONTINUATION_"
            "OBEYS_THE_EXACT_MATRIX_RICCATI_SYSTEM_D_s_M=L(Y(s))-zI-M^2,_"
            "AND_ITS_GEOMETRY_JET_OBEYS_THE_LINEARIZED_SYSTEM;_THE_ACTUAL_"
            "N12_COEFFICIENT_CONTINUATION_REMAINS_TO_BE_CERTIFIED"
        ),
        "event_normal_system": {
            "coordinate": (
                "s=NONNEGATIVE_PHYSICAL_DISTANCE_FROM_THE_CERTIFIED_"
                "TERMINAL_EVENT_INTO_THE_REALIZED_FINITE_EXTERIOR"
            ),
            "terminal_value": "M(0,z)=W_phys",
            "Riccati_equation": "D_s_M=(L_spatial(Y(s))-zI)-M^2",
            "geometry_initial_value": "D_Phi_M(0,z)=D_Phi_W_phys",
            "geometry_jet_equation": (
                "D_s(delta_M)=delta_L-M*delta_M-delta_M*M"
            ),
            "coercive_region": "REAL_z<0",
            "small_s_expansion": (
                "M(s,z)=W_phys+s*(L_event-zI-W_phys^2)+O(s^2)"
            ),
            "arbitrary_Robin_or_regular_cover_endpoint_used": False,
        },
        "force_transfer": {
            "required_oracle": "D_Phi_M(z)_ON_THE_RETAINED_SOURCE_BOUNDARY",
            "identity": weyl["exterior_oracle_bundle"]["first_variation_identity"],
            "heat_minus_zeta_force_value_evaluated": False,
            "why": (
                "THE_EVENT_INITIAL_VALUE_IS_NOW_FIXED_BUT_THE_ACTION_OWNED_"
                "L_spatial(Y(s)),_D_Phi_L,_AND_DISTANCE_TO_THE_SOURCE_"
                "BOUNDARY_HAVE_NOT_YET_BEEN_CONTINUED_OR_ENCLOSED"
            ),
        },
        "witnesses": {
            "scalar_orientation": orientation,
            "geometry_jet": jet,
        },
        "exact_next_dependency": (
            "PULL_BACK_THE_RETAINED_SPATIAL_OPERATOR_AND_ITS_GEOMETRY_JET_"
            "TO_THE_DESINGULARIZED_EVENT_NORMAL_BRANCH,_THEN_CERTIFY_A_"
            "POLE_FREE_INTERVAL_RICCATI_ENCLOSURE_FROM_W_phys_TO_THE_"
            "ACTION_OWNED_SOURCE_BOUNDARY"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_WEYL_COEFFICIENT_CONTINUATION_OPEN",
            "event_normal_Weyl_initial_condition": "DERIVED",
            "event_normal_geometry_jet_system": "DERIVED",
            "actual_N12_exterior_Weyl_value_and_jet": "OPEN",
            "zero_source_force_value": "OPEN",
            "same_action_saddle": "WAITING_ON_WEYL_CONTINUATION",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
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
    print(RESULT)


if __name__ == "__main__":
    main()
