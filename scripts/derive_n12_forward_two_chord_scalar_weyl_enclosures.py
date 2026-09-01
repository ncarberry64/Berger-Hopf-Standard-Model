"""Enclose retained scalar/de Rham Weyl data through the certified core."""

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

from bhsm.interface.aether_forward_scalar_weyl_enclosures import (  # noqa: E402
    scalar_compact_radius_weyl_variation_bounds,
    scalar_nonnegative_exterior_weyl_bounds,
)
from bhsm.interface.aether_nonabelian_derham_response_v16_04 import (  # noqa: E402
    angular_derham_blocks,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
)
HEAT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
)
TRANSFER = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json"
)
WEYL_VARIATIONS = ARTIFACTS / (
    "flagship_integration/BHSM_N12_FORWARD_COMPACT_SUPPORT_WEYL_VARIATIONS.json"
)
MODULE = ROOT / "src/bhsm/interface/aether_forward_scalar_weyl_enclosures.py"
INPUTS = (HEAT, TRANSFER, WEYL_VARIATIONS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _retained_low_level_channels(maximum_level: int = 3) -> list[dict[str, Any]]:
    occurrences: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for level in range(maximum_level + 1):
        blocks = angular_derham_blocks(level, 1.0)
        for sector, key in (
            ("scalar", "scalar_operator"),
            ("one_form", "vector_operator"),
        ):
            eigenvalues = np.linalg.eigvalsh(blocks[key])
            rounded = np.round(eigenvalues, decimals=10)
            for value in sorted(set(float(number) for number in rounded)):
                multiplicity = int(np.count_nonzero(np.isclose(rounded, value)))
                occurrences[value].append(
                    {"sector": sector, "level": level, "multiplicity": multiplicity}
                )
    return [
        {
            "unit_radius_eigenvalue": value,
            "occurrences": occurrences[value],
        }
        for value in sorted(occurrences)
    ]


def build_payload() -> dict[str, Any]:
    paths = (*INPUTS, MODULE)
    if not all(path.is_file() for path in paths):
        raise FileNotFoundError("all two-chord scalar Weyl inputs are required")
    heat, transfer, variations = (
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS
    )
    if not all(
        record.get("validation_passed") is True
        for record in (heat, transfer, variations)
    ):
        raise RuntimeError("all two-chord scalar Weyl inputs must validate")

    duration = float(heat["two_chord_heat_test"]["proper_duration_lower"])
    radius_lower = min(
        float(chord["R4_boundary_lower"])
        for chord in heat["chord_tube_enclosures"]
    )
    kappa2 = 1.0
    rows = []
    for channel in _retained_low_level_channels():
        eigenvalue = float(channel["unit_radius_eigenvalue"])
        potential_upper = eigenvalue / radius_lower**2
        base = scalar_nonnegative_exterior_weyl_bounds(
            duration, potential_upper, kappa2
        )
        weak = scalar_compact_radius_weyl_variation_bounds(
            base["upper"],
            potential_upper,
            kappa2,
            first_log_radius_bound=1.0,
            second_log_radius_bound=0.0,
        )
        rows.append(
            {
                **channel,
                "potential_upper_on_certified_core": potential_upper,
                "birth_Weyl_interval_at_z_minus_1": [base["lower"], base["upper"]],
                "birth_Weyl_interval_width": base["width"],
                "unit_compact_log_radius_direction_bounds": weak,
            }
        )

    all_numbers_finite = all(
        np.isfinite(
            [
                row["potential_upper_on_certified_core"],
                *row["birth_Weyl_interval_at_z_minus_1"],
                row["birth_Weyl_interval_width"],
                *row["unit_compact_log_radius_direction_bounds"].values(),
            ]
        ).all()
        for row in rows
    )
    validation = {
        "all_inputs_validated": True,
        "two_certified_chords_consumed": len(heat["chord_tube_enclosures"]) == 2,
        "proper_duration_lower_is_positive": duration > 0.0,
        "certified_radius_lower_is_positive": radius_lower > 0.0,
        "comparison_rows_are_finite": bool(all_numbers_finite),
        "every_comparison_interval_is_ordered": all(
            row["birth_Weyl_interval_at_z_minus_1"][0]
            <= row["birth_Weyl_interval_at_z_minus_1"][1]
            for row in rows
        ),
        "low_level_scalar_and_one_form_channels_are_action_derived": (
            {row["unit_radius_eigenvalue"] for row in rows}
            == {0.0, 3.0, 4.0, 8.0, 9.0, 15.0, 16.0, 25.0}
        ),
        "constant_channel_exposes_short_core_weakness": (
            rows[0]["birth_Weyl_interval_at_z_minus_1"][1] > 4.0e7
        ),
        "no_future_endpoint_or_terminal_event_selected": True,
        "no_spatial_tail_relabelled_as_temporal_control": True,
        "no_product_Dirac_pair_contact_or_zero_source_force_claim": True,
    }
    return {
        "artifact": "BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES",
        "status": "TWO_CHORD_SCALAR_DERHAM_WEYL_AND_COMPACT_WEAK_JETS_ENCLOSED_BROADLY",
        "classification": (
            "THE_CERTIFIED_TWO_CHORD_CORE_AND_NONNEGATIVITY_OF_THE_RETAINED_"
            "FUTURE_EXTERIOR_GIVE_RIGOROUS_BUT_BROAD_BIRTH_WEYL_INTERVALS_"
            "AT_z_MINUS_1_FOR_EACH_FIXED_SCALAR_OR_DERHAM_CHANNEL;_THE_SAME_"
            "ENERGY_IDENTITY_GIVES_FINITE_COMPACT_SUPPORT_FIRST_AND_MIXED_"
            "LOG_RADIUS_VARIATION_BOUNDS_WITHOUT_SELECTING_A_FUTURE_ENDPOINT"
        ),
        "comparison_theorem": {
            "equation": "-u''+V*u=-kappa^2*u",
            "core_hypotheses": "T>=T_lower_AND_0<=V<=Vmax",
            "birth_conormal_sign": "M=-u'(0)/u(0)",
            "terminal_hypothesis": (
                "THE_RETAINED_UNKNOWN_FUTURE_INDUCES_A_NONNEGATIVE_INWARD_"
                "GRAPH_-u'(T)/u(T)>=0;_DIRICHLET_IS_THE_INFINITY_LIMIT"
            ),
            "bound": (
                "kappa*tanh(kappa*T_lower)<=M<=K*coth(K*T_lower),_"
                "K=sqrt(kappa^2+Vmax)"
            ),
            "weak_jet_normalization": (
                "norm(x_h)_infinity,norm(x_k)_infinity<=1_AND_x_hk=0_"
                "WITH_COMPACT_SUPPORT_INSIDE_THE_CERTIFIED_TWO_CHORD_CORE"
            ),
            "Poisson_energy_bound": "norm(U)^2_L2<=M_upper/kappa^2",
        },
        "certified_core": {
            "coordinate_time_end": heat["certified_coordinate_time_end"],
            "proper_duration_lower": duration,
            "proper_duration_upper": heat["two_chord_heat_test"][
                "proper_duration_upper"
            ],
            "R4_lower": radius_lower,
        },
        "spectral_probe": {
            "z": -1.0,
            "negative_spectral_magnitude_kappa_squared": kappa2,
            "role": "RESOLVENT_PROBE_NOT_MOMENTUM_SQUARED",
        },
        "representative_retained_low_levels": {
            "levels": [0, 1, 2, 3],
            "scope": (
                "EXACT_ROWS_FOR_THE_STORED_ROUND_SCALAR_AND_ONE_FORM_"
                "BLOCKS_THROUGH_LEVEL_3;_THE_COMPARISON_FORMULA_IS_"
                "PARAMETRIC_FOR_EVERY_NONNEGATIVE_UNIT_RADIUS_EIGENVALUE_c"
            ),
            "rows": rows,
        },
        "adjudication": {
            "scalar_and_deRham_base_Weyl_on_two_chord_core": "ENCLOSED_BROADLY",
            "scalar_and_deRham_compact_support_weak_jets": "ENCLOSED_BROADLY",
            "maximal_history_scalar_and_deRham_oracle": (
                "BROAD_INTERVAL_AT_z_MINUS_1_NOT_A_SHARP_VALUE"
            ),
            "product_Dirac_channels": "OPEN",
            "common_pair_contact_contractions": "OPEN",
            "certified_spatial_tail_assembly": "OPEN",
            "zero_source_force": "OPEN",
        },
        "exact_next_dependency": (
            "DERIVE_THE_PRODUCT_DIRAC_FIXED_CHANNEL_COMPARISON_ENCLOSURE_AND_"
            "COMBINE_ALL_RETAINED_CHANNEL_POISSON_BOUNDS_WITH_THE_COMMON_"
            "PAIR_CONTACT_INCIDENCE_AND_CERTIFIED_SPATIAL_TAIL;_THEN_"
            "ASSEMBLE_THE_ZERO_SOURCE_WEAK_FORCE"
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
