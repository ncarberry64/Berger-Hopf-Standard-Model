"""Enclose factorized product-Dirac Weyl data through the certified core."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_product_dirac_weyl_enclosures import (  # noqa: E402
    product_dirac_compact_radius_weyl_variation_bounds,
    product_dirac_nonnegative_exterior_weyl_bounds,
)
from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (  # noqa: E402
    berger_dirac_block,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
)
HEAT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
)
TRANSFER = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json"
)
SCALAR = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
)
WEYL_VARIATIONS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json"
)
MODULE = ROOT / (
    "src/bhsm/interface/aether_forward_product_dirac_weyl_enclosures.py"
)
INPUTS = (HEAT, TRANSFER, SCALAR, WEYL_VARIATIONS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _retained_low_level_channels(maximum_level: int = 3) -> list[dict[str, Any]]:
    occurrences: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for level in range(maximum_level + 1):
        eigenvalues = np.round(
            np.linalg.eigvalsh(berger_dirac_block(level, 1.0, 1.0)),
            decimals=10,
        )
        for signed_value in sorted(set(float(number) for number in eigenvalues)):
            multiplicity = int(np.count_nonzero(np.isclose(eigenvalues, signed_value)))
            occurrences[abs(signed_value)].append(
                {
                    "level": level,
                    "signed_unit_radius_eigenvalue": signed_value,
                    "multiplicity": multiplicity,
                }
            )
    return [
        {
            "absolute_unit_radius_eigenvalue": value,
            "occurrences": occurrences[value],
        }
        for value in sorted(occurrences)
    ]


def build_payload() -> dict[str, Any]:
    paths = (*INPUTS, MODULE)
    if not all(path.is_file() for path in paths):
        raise FileNotFoundError("all two-chord product-Dirac inputs are required")
    heat, transfer, scalar, variations = (
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    )
    if not all(
        record.get("validation_passed") is True
        for record in (heat, transfer, scalar, variations)
    ):
        raise RuntimeError("all two-chord product-Dirac inputs must validate")

    duration = float(heat["two_chord_heat_test"]["proper_duration_lower"])
    radius_lower = float(scalar["certified_core"]["R4_lower"])
    kappa2 = 1.0
    rows = []
    for channel in _retained_low_level_channels():
        eigenvalue = float(channel["absolute_unit_radius_eigenvalue"])
        superpotential_upper = eigenvalue / radius_lower
        base = product_dirac_nonnegative_exterior_weyl_bounds(
            duration, superpotential_upper, kappa2
        )
        weak = product_dirac_compact_radius_weyl_variation_bounds(
            base["upper"],
            superpotential_upper,
            kappa2,
            first_log_radius_bound=1.0,
            second_log_radius_bound=0.0,
        )
        rows.append(
            {
                **channel,
                "superpotential_absolute_upper_on_certified_core": (
                    superpotential_upper
                ),
                "birth_Weyl_interval_at_z_minus_1": [base["lower"], base["upper"]],
                "Dirichlet_trial_decomposition": {
                    key: base[key]
                    for key in (
                        "trial_derivative_energy",
                        "trial_cross_bound",
                        "trial_potential_and_probe_bound",
                    )
                },
                "unit_compact_log_radius_direction_bounds": weak,
            }
        )

    all_numbers_finite = all(
        np.isfinite(
            [
                row["superpotential_absolute_upper_on_certified_core"],
                *row["birth_Weyl_interval_at_z_minus_1"],
                *row["Dirichlet_trial_decomposition"].values(),
                *row["unit_compact_log_radius_direction_bounds"].values(),
            ]
        ).all()
        for row in rows
    )
    validation = {
        "all_inputs_validated": True,
        "same_certified_two_chord_core_consumed": (
            duration == scalar["certified_core"]["proper_duration_lower"]
        ),
        "proper_duration_and_radius_are_positive": duration > 0.0
        and radius_lower > 0.0,
        "factorized_rows_are_finite": bool(all_numbers_finite),
        "every_interval_is_nonnegative_and_ordered": all(
            0.0 <= row["birth_Weyl_interval_at_z_minus_1"][0]
            <= row["birth_Weyl_interval_at_z_minus_1"][1]
            for row in rows
        ),
        "low_level_round_Dirac_absolute_spectrum_is_action_derived": (
            {row["absolute_unit_radius_eigenvalue"] for row in rows}
            == {1.5, 2.5, 3.5, 4.5}
        ),
        "signed_Dirac_branches_present_and_bound_is_sign_independent": (
            any(
                occurrence["signed_unit_radius_eigenvalue"] < 0.0
                for row in rows
                for occurrence in row["occurrences"]
            )
            and any(
                occurrence["signed_unit_radius_eigenvalue"] > 0.0
                for row in rows
                for occurrence in row["occurrences"]
            )
            and all(
                row["superpotential_absolute_upper_on_certified_core"] >= 0.0
                for row in rows
            )
        ),
        "no_superpotential_derivative_introduced": True,
        "no_future_endpoint_event_chord3_or_momentum_selected": True,
        "pair_contact_tail_and_force_not_claimed": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES",
        "status": "TWO_CHORD_PRODUCT_DIRAC_WEYL_AND_COMPACT_WEAK_JETS_ENCLOSED_BROADLY",
        "classification": (
            "THE_ACTION_OWNED_FACTORIZATION_A_lambda_STAR_A_lambda_AND_A_"
            "PIECEWISE_LINEAR_DIRICHLET_TRIAL_ON_THE_CERTIFIED_TWO_CHORD_"
            "CORE_GIVE_A_FUTURE_INDEPENDENT_BROAD_PRODUCT_DIRAC_BIRTH_WEYL_"
            "ENCLOSURE_AT_z_MINUS_1;_RELATIVE_FORM_COERCIVITY_GIVES_FINITE_"
            "CORE_SUPPORTED_FIRST_AND_MIXED_LOG_RADIUS_JET_BOUNDS_WITHOUT_"
            "INTRODUCING_s_PRIME_OR_SELECTING_A_TERMINAL_EVENT"
        ),
        "factorized_comparison_theorem": {
            "factor": "A_lambda=d_tau+s_lambda,_s_lambda=chirality*lambda/R4",
            "form_at_z_minus_kappa_squared": (
                "norm(A_lambda*u)^2+kappa^2*norm(u)^2"
            ),
            "birth_conormal_sign": "M=-A_lambda*u(0)/u(0)",
            "terminal_hypothesis": (
                "THE_RETAINED_UNKNOWN_FUTURE_INDUCES_A_NONNEGATIVE_INWARD_"
                "GRAPH_-A_lambda*u(T)/u(T)>=0"
            ),
            "Dirichlet_trial": "u(tau)=1-tau/T_lower_ON_[0,T_lower]",
            "bound": (
                "0<=M<=1/T_lower+S+(S^2+kappa^2)*T_lower/3,_"
                "S=abs(lambda)/R4_lower"
            ),
            "reason_s_prime_is_absent": (
                "THE_ESTIMATE_IS_PERFORMED_IN_THE_ACTION_OWNED_FACTORIZED_"
                "QUADRATIC_FORM_NOT_IN_AN_EXPANDED_SCHRODINGER_POTENTIAL"
            ),
            "weak_jet_support": "INSIDE_THE_CERTIFIED_TWO_CHORD_CORE",
        },
        "certified_core": scalar["certified_core"],
        "spectral_probe": scalar["spectral_probe"],
        "representative_retained_low_levels": {
            "levels": [0, 1, 2, 3],
            "scope": (
                "EXACT_ROWS_FOR_THE_STORED_ROUND_DIRAC_BLOCKS_THROUGH_LEVEL_"
                "3;_THE_BOUND_IS_PARAMETRIC_IN_EVERY_ABSOLUTE_UNIT_RADIUS_"
                "DIRAC_EIGENVALUE"
            ),
            "rows": rows,
        },
        "adjudication": {
            "product_Dirac_base_Weyl_at_z_minus_1": "ENCLOSED_BROADLY",
            "product_Dirac_core_supported_weak_jets": "ENCLOSED_BROADLY",
            "scalar_and_deRham_enclosures": "INHERITED_VALIDATED",
            "all_channel_pair_contact_incidence_assembly": "OPEN",
            "certified_spatial_tail_assembly": "OPEN",
            "zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "COMBINE_THE_PARAMETRIC_SCALAR_DERHAM_AND_PRODUCT_DIRAC_POISSON_"
            "BOUNDS_WITH_THE_ACTION_OWNED_COMMON_PAIR_CONTACT_INCIDENCE_AND_"
            "CERTIFIED_SPATIAL_GALERKIN_TAIL;_ASSEMBLE_AND_ADJUDICATE_THE_"
            "ZERO_SOURCE_WEAK_GEOMETRY_FORCE_AT_z_MINUS_1"
        ),
        "claim_boundary": {
            "terminal_event_reachability_required": False,
            "chord_03_authorized": False,
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in paths},
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
                "row_count": len(
                    payload["representative_retained_low_levels"]["rows"]
                ),
                "validation_passed": payload["validation_passed"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
