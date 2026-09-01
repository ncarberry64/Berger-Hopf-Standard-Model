"""Audit the retained heat-tail estimate after two certified Gate-7 chords.

The earlier cover-tail audit predates the two 1e-8 exact shadowing
certificates.  This replay consumes those certificates and encloses lapse and
boundary R4 on both complete chord tubes in the existing action norm.  It
does not infer a temporal tail from the certified spatial Galerkin tail.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import (
    RADIUS0,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/intrinsic_state_selection"
FLAGSHIP = ROOT / "artifacts/flagship_integration"
CHORDS = (
    {
        "name": "chord_01",
        "certificate": BASE
        / "BHSM_N12_GATE7_COMPLETE_PHYSICAL_U_GREEN_SHADOWING.json",
        "domain": BASE / "BHSM_N12_FIRST_CHORD_HERMITE_SPAN_DOMAIN.json",
        "center": BASE
        / "BHSM_N12_FIRST_CHORD_HIGH_PRECISION_HERMITE_CENTER.npz",
    },
    {
        "name": "chord_02",
        "certificate": BASE / "BHSM_N12_GATE7_CHORD_02_SIGNED_ALIGNED_GREEN.json",
        "domain": BASE / "BHSM_N12_CHORD_02_HERMITE_SPAN_DOMAIN.json",
        "center": BASE / "BHSM_N12_CHORD_02_HIGH_PRECISION_HERMITE_CENTER.npz",
    },
)
SUPERDET = ROOT / "artifacts/BHSM_aether_common_quantum_superdeterminant_v15_96.json"
RESULT = FLAGSHIP / "BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
ORDER = 12
CHORD_DURATION = 1.0e-8
HEAT_LENGTH = 1.0
INFLATION = 1.0 + 1.0e-10


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() == ".json":
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def _up(value: float) -> float:
    return math.nextafter(float(value) * INFLATION, math.inf)


def _down(value: float) -> float:
    return math.nextafter(float(value) / INFLATION, 0.0)


def _r4(coordinates: np.ndarray) -> float:
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    u_boundary = float(coordinates[1 : 1 + ORDER] @ signs_k)
    b_boundary = float(
        coordinates[1 + 2 * ORDER : 1 + 3 * ORDER] @ signs_j
    )
    radius = RADIUS0 * math.exp(float(coordinates[0]))
    a_boundary = radius * math.exp(u_boundary + b_boundary) / math.sqrt(2.0)
    b_radius = radius * math.exp(u_boundary - b_boundary) / math.sqrt(2.0)
    return float(
        a_boundary
        * b_radius
        / math.sqrt(a_boundary**2 + b_radius**2)
    )


def _green_radius(certificate: dict[str, object]) -> float:
    rows = certificate["rows"]
    values = []
    for row in rows:
        key = (
            "piecewise_physical_u_Green_radius_upper"
            if "piecewise_physical_u_Green_radius_upper" in row
            else "piecewise_Green_radius_upper"
        )
        values.append(float(row[key]))
    return max(values)


def build_payload() -> dict[str, object]:
    paths = (
        SUPERDET,
        *(item[key] for item in CHORDS for key in ("certificate", "domain", "center")),
    )
    if not all(path.is_file() for path in paths):
        raise FileNotFoundError("all two-chord heat-tail inputs are required")

    superdet = json.loads(SUPERDET.read_text(encoding="utf-8"))
    if superdet.get("validation_passed") is not True:
        raise RuntimeError("validated retained common heat functional required")

    dims = dimensions(ORDER)
    qdim = dims["coordinates"]
    frequencies = spectral_frequencies(ORDER)
    q_weights = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weights = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    lapse_trace_dual = float(np.linalg.norm(1.0 / m_weights[:ORDER]))
    r4_trace_dual = float(
        math.sqrt(
            1.0 / q_weights[0] ** 2
            + np.sum(1.0 / q_weights[1 : 1 + ORDER] ** 2)
            + np.sum(
                1.0 / q_weights[1 + 2 * ORDER : 1 + 3 * ORDER] ** 2
            )
        )
    )
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)

    rows = []
    previous_end = 0.0
    for item in CHORDS:
        certificate = json.loads(item["certificate"].read_text(encoding="utf-8"))
        domain = json.loads(item["domain"].read_text(encoding="utf-8"))
        if not (
            certificate.get("validation_passed") is True
            and domain.get("validation_passed") is True
        ):
            raise RuntimeError(f"validated {item['name']} inputs required")

        interval = [float(value) for value in domain["span"]["coordinate_time_interval"]]
        if interval[0] != previous_end or interval[1] - interval[0] != CHORD_DURATION:
            raise RuntimeError("the two certified chord intervals must be contiguous")
        previous_end = interval[1]

        data = np.load(item["center"])
        weights = np.asarray(data["action_weights"], dtype=float)
        x0, x1 = np.asarray(data["endpoint_action_states"], dtype=float)
        f0, f1 = np.asarray(data["endpoint_action_rates"], dtype=float)
        delta = x1 - x0
        projection = np.column_stack(
            (0.5 * delta, CHORD_DURATION * f0 - delta, -(CHORD_DURATION * f1 - delta))
        )
        hermite_action_radius = _up(float(np.linalg.norm(projection, ord=2)))
        green_action_radius = _up(_green_radius(certificate))
        complete_tube_radius = _up(hermite_action_radius + green_action_radius)

        midpoint = 0.5 * (x0 + x1) / weights
        lapse_midpoint = math.exp(float(midpoint[2 * qdim : 2 * qdim + ORDER] @ signs_k))
        r4_midpoint = _r4(midpoint[:qdim])
        lapse_lower = _down(
            lapse_midpoint * math.exp(-complete_tube_radius * lapse_trace_dual)
        )
        lapse_upper = _up(
            lapse_midpoint * math.exp(complete_tube_radius * lapse_trace_dual)
        )
        r4_lower = _down(r4_midpoint * math.exp(-complete_tube_radius * r4_trace_dual))
        r4_upper = _up(r4_midpoint * math.exp(complete_tube_radius * r4_trace_dual))

        rows.append(
            {
                "chord": item["name"],
                "coordinate_time_interval": interval,
                "hermite_span_action_radius_upper": hermite_action_radius,
                "Green_shadow_action_radius_upper": green_action_radius,
                "complete_action_tube_radius_upper": complete_tube_radius,
                "boundary_lapse_midpoint": lapse_midpoint,
                "boundary_lapse_lower": lapse_lower,
                "boundary_lapse_upper": lapse_upper,
                "R4_boundary_midpoint": r4_midpoint,
                "R4_boundary_lower": r4_lower,
                "R4_boundary_upper": r4_upper,
                "proper_duration_lower": _down(CHORD_DURATION * lapse_lower),
                "proper_duration_upper": _up(CHORD_DURATION * lapse_upper),
            }
        )

    proper_lower = _down(math.fsum(row["proper_duration_lower"] for row in rows))
    proper_upper = _up(math.fsum(row["proper_duration_upper"] for row in rows))
    r4_lower = min(float(row["R4_boundary_lower"]) for row in rows)
    r4_upper = max(float(row["R4_boundary_upper"]) for row in rows)
    gap_lower = _down(1.0 / r4_upper)
    gap_upper = _up(1.0 / r4_lower)

    # The endpoint expression decreases with both mu and T for mu,T>0.
    # Evaluating it at their certified upper bounds is therefore the most
    # optimistic value allowed by this two-chord enclosure.  If even that is
    # large, the estimate is noninformative everywhere in the enclosure.
    optimistic_endpoint_bound = _down(
        2.0 * gap_upper / math.expm1(2.0 * gap_upper * proper_upper)
    )
    weakest_suppression = _down(math.exp(-2.0 * gap_upper * proper_upper))
    validation = {
        "two_certified_chords_consumed": previous_end == 2.0e-8,
        "both_chord_and_domain_artifacts_validate": True,
        "Hermite_and_Green_radii_combined_in_same_action_norm": all(
            row["complete_action_tube_radius_upper"] > 0.0 for row in rows
        ),
        "lapse_and_R4_trace_enclosures_finite": all(
            row[key] > 0.0
            for row in rows
            for key in (
                "boundary_lapse_lower",
                "boundary_lapse_upper",
                "R4_boundary_lower",
                "R4_boundary_upper",
            )
        ),
        "proper_duration_remains_below_one_heat_length": proper_upper < HEAT_LENGTH,
        "best_case_exponential_suppression_is_negligible": weakest_suppression > 0.9999999,
        "best_case_endpoint_bound_remains_noninformative": optimistic_endpoint_bound > 1.0e7,
        "spatial_Galerkin_tail_not_relabelled_as_temporal_tail": True,
        "chord_03_not_authorized_by_heat_tail_estimate": True,
        "no_equation_gate_scale_fit_endpoint_or_physics_added": True,
    }
    payload = {
        "artifact": "BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT",
        "classification": (
            "TWO_CERTIFIED_CHORDS_EXTEND_THE_RIGOROUS_FORWARD_CORE_TO_2E-8_"
            "BUT_DO_NOT_CONTROL_THE_RETAINED_TEMPORAL_HEAT_TAIL;_EVEN_THE_"
            "MOST_OPTIMISTIC_CERTIFIED_ENDPOINT_BOUND_EXCEEDS_1E7"
        ),
        "current_flagship_gate": 7,
        "certified_coordinate_time_end": previous_end,
        "chord_tube_enclosures": rows,
        "two_chord_heat_test": {
            "proper_duration_lower": proper_lower,
            "proper_duration_upper": proper_upper,
            "proper_duration_over_heat_length_upper": proper_upper / HEAT_LENGTH,
            "retained_heat_length_in_ell_kappa_units": HEAT_LENGTH,
            "boundary_lapse_trace_dual_norm": lapse_trace_dual,
            "boundary_log_R4_global_trace_dual_norm": r4_trace_dual,
            "smallest_nonzero_sector_gap_lower": gap_lower,
            "smallest_nonzero_sector_gap_upper": gap_upper,
            "best_case_exp_minus_2_gap_T": weakest_suppression,
            "best_case_constant_gap_endpoint_bound_lower": optimistic_endpoint_bound,
            "endpoint_bound_formula": "2*mu/(exp(2*mu*T)-1)",
        },
        "adjudication": {
            "finite_certified_core_valid": True,
            "spatial_Galerkin_tail_certified": True,
            "temporal_state_or_source_tail_certified": False,
            "two_chord_finite_core_promotable_to_complete_heat_response": False,
            "chord_03_has_proof_value_from_this_estimate": False,
            "chord_03_authorized": False,
            "retained_action_obstruction_proved": False,
            "failure_class": "MISSING_GLOBAL_TEMPORAL_CONTROL_IDENTITY",
        },
        "exact_next_dependency": (
            "PROVE_A_TEMPORAL_ABSORBING_OR_INTEGRATED_TRANSPORT_BOUND_WITH_"
            "UNIFORM_EXISTING_DOMAIN_MARGINS,_OR_CERTIFY_A_FIRST_RETAINED_"
            "TERMINAL_EVENT_OR_PHYSICAL_DOMAIN_EXIT_AND_ITS_SOURCE_GRAPH"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in paths},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    return payload


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
                "classification": payload["classification"],
                "proper_duration_upper": payload["two_chord_heat_test"][
                    "proper_duration_upper"
                ],
                "best_case_endpoint_bound_lower": payload[
                    "two_chord_heat_test"
                ]["best_case_constant_gap_endpoint_bound_lower"],
                "validation_passed": payload["validation_passed"],
                "sha256": _sha256(RESULT),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
