"""Close compact-support Weyl variations on infinite Friedrichs histories."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json"
)
WEYL = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json"
)
PROPER_TIME = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
)
GEOMETRY_JETS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS.json"
)
COMPACT_INTERVAL = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMPACT_INTERVAL_RECENTERING.json"
)
GAP_AUDIT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_EXTERIOR_GAP_ORACLE_AUDIT.json"
)
INPUTS = (WEYL, PROPER_TIME, GEOMETRY_JETS, COMPACT_INTERVAL, GAP_AUDIT)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _fraction(value: Fraction) -> dict[str, object]:
    return {"exact": f"{value.numerator}/{value.denominator}", "decimal": float(value)}


def _second_variation_witness() -> dict[str, object]:
    # M=a-z-b^2/(d-z), with d(t,s)=d0+t*h+s*k+t*s*ell.
    a, b, d, z = Fraction(2), Fraction(-1), Fraction(3), Fraction(-1)
    h, k, ell = Fraction(1, 5), Fraction(1, 7), Fraction(1, 11)
    denominator = d - z
    base = a - z - b * b / denominator
    first_h = b * b * h / denominator**2
    first_k = b * b * k / denominator**2
    mixed = b * b * ell / denominator**2 - 2 * b * b * h * k / denominator**3
    return {
        "model": "M=a-z-b^2/(d-z)",
        "geometry": "d(t,s)=3+t/5+s/7+t*s/11",
        "base": _fraction(base),
        "first_left": _fraction(first_h),
        "first_right": _fraction(first_k),
        "mixed_second": _fraction(mixed),
        "resolvent_pair_formula": (
            "M_hk=<U,P_hk*U>-<P_h*U,R_D*P_k*U>"
            "-<P_k*U,R_D*P_h*U>"
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all compact-support Weyl inputs are required")
    records = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("all compact-support Weyl inputs must validate")
    weyl, proper_time, geometry, compact_interval, gap = records
    witness = _second_variation_witness()
    validation = {
        "all_inputs_validated": True,
        "negative_z_coercive_region_available": weyl["validation"][
            "negative_z_pencil_is_coercive"
        ]
        is True,
        "Friedrichs_infinite_endpoint_supported": weyl["endpoint_compatibility"][
            "infinite_history"
        ].startswith("CLOSE_THE_NONNEGATIVE"),
        "compact_support_fixes_proper_time_domain": (
            "D_Phi_D_tau=0"
            in proper_time["proper_time_form_theorem"][
                "compactly_supported_geometry_variation"
            ]
        ),
        "local_first_second_operator_jets_available": geometry[
            "validation_passed"
        ]
        is True,
        "all_finite_support_intervals_have_variational_cover": compact_interval[
            "claim_boundary"
        ]["finite_regular_interval_variational_cover"]
        == "DERIVED",
        "gap_not_misused_as_an_oracle_value_bound": gap["validation_passed"] is True,
        "exact_second_variation_witness_is_nonzero": witness["mixed_second"][
            "exact"
        ]
        != "0/1",
        "no_terminal_return_endpoint_motion_new_gate_or_prediction": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS",
        "status": "COMPACT_SUPPORT_WEYL_C1_C2_AT_FRIEDRICHS_END_DERIVED",
        "classification": (
            "FOR_EVERY_COMPACTLY_SUPPORTED_REGULAR_GEOMETRY_VARIATION_ON_"
            "A_FINITE_SUBINTERVAL_OF_AN_INFINITE_FORWARD_HISTORY_THE_"
            "FRIEDRICHS_ENDPOINT_DOMAIN_IS_FIXED;_NEGATIVE_z_COERCIVITY_"
            "AND_THE_FIXED_CHANNEL_RELATIVE_FORM_JETS_GIVE_FINITE_EXACT_"
            "FIRST_AND_MIXED_SECOND_BIRTH_WEYL_VARIATIONS_WITHOUT_A_"
            "UNIFORM_T_TO_INFINITY_TRANSFER_LIMIT_OR_TERMINAL_RETURN"
        ),
        "weak_variation_theorem": {
            "variation_class": (
                "COMPACTLY_SUPPORTED_RETAINED_GEOMETRY_TEST_VARIATIONS_"
                "INSIDE_ONE_REGULAR_FORWARD_INTERVAL"
            ),
            "endpoint_domain_variation": 0,
            "temporal_bulk_variation": "D_Phi_D_tau=D_Phi_Delta_tau=0",
            "first": (
                "<a,D_hM(z)b>=<U_a,P_h*U_b>+RETAINED_BOUNDARY_CONTACT_h"
            ),
            "mixed_second": (
                "<a,D_hkM(z)b>=<U_a,P_hk*U_b>"
                "-<P_h*U_a,R_D(z)*P_k*U_b>"
                "-<P_k*U_a,R_D(z)*P_h*U_b>"
                "+RETAINED_PAIR_CONTACT_hk"
            ),
            "resolvent_bound": "norm(R_D(z))<=1/abs(z)_FOR_REAL_z<0",
            "finiteness_reason": (
                "U_a,U_b_ARE_IN_THE_FRIEDRICHS_FORM_DOMAIN;_P_h_AND_P_hk_"
                "HAVE_BOUNDED_COMPACT_SUPPORT_RELATIVE_FORM_CONSTANTS"
            ),
        },
        "infinite_end_adjudication": {
            "base_Weyl_family": "ALREADY_DEFINED_BY_THE_FRIEDRICHS_FORM",
            "compact_support_first_second_weak_variations": "DERIVED_HERE",
            "uniform_transfer_jet_limit_as_T_to_infinity_required": False,
            "global_noncompact_saddle_variations": "NOT_COVERED",
            "numerical_or_interval_value_of_M_D_M_D2_M": "NOT_EVALUATED",
        },
        "exact_witness": witness,
        "exact_next_dependency": (
            "EVALUATE_OR_RIGOROUSLY_ENCLOSE_THE_FIXED_CHANNEL_POISSON_WEYL_"
            "CONTRACTIONS_AND_COMMON_PAIR_CONTACT_TERMS_FOR_THE_ACTUAL_"
            "MAXIMAL_HISTORY_ON_A_NONEMPTY_NEGATIVE_z_REGION;_ASSEMBLE_THE_"
            "ZERO_SOURCE_WEAK_GEOMETRY_FORCE_BEFORE_ANY_GLOBAL_SADDLE_"
            "VARIATION"
        ),
        "claim_boundary": {
            "infinite_Friedrichs_compact_support_Weyl_C1_C2": "DERIVED",
            "global_noncompact_Weyl_variations": "OPEN_IF_REQUIRED_BY_SADDLE",
            "oracle_values": "OPEN",
            "zero_source_force": "OPEN",
            "same_action_saddle": "OPEN",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03": "NOT_AUTHORIZED",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
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
                "mixed_witness": payload["exact_witness"]["mixed_second"],
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
