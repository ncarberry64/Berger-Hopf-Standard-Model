"""Materialize the AE4 stop-matched center Calderon diagnostic."""

from __future__ import annotations

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_current_c2_factorized_hs_calderon import (
    ACTION_VERSION,
    factorized_product_dirac_hs_weyl_jet,
)
from bhsm.interface.ae4_current_c2_stop_matched_center_diagnostic import (
    CLASSIFICATION,
    refine_piecewise_linear_path,
    stop_matched_center_proper_time_path,
)


A = ROOT / "artifacts/action_extension"
F = ROOT / "artifacts/flagship_integration"
CENTER = F / "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.json"
CENTER_DATA = CENTER.with_suffix(".npz")
FIRST_HIT = F / "BHSM_N12_GATE7_EXACT_AFFINE_TERMINAL_INTERVAL_NEWTON_FIRST_HIT.json"
DOMAIN = A / "BHSM_AE4_CURRENT_C2_CANONICAL_STOP_DOMAIN_BRIDGE.json"
FACTORIZED = A / "BHSM_AE4_CURRENT_C2_FACTORIZED_HS_CALDERON.json"
TARGET = A / "BHSM_AE4_CURRENT_C2_STOP_MATCHED_CENTER_DIAGNOSTIC.json"
INPUTS = (
    CENTER,
    CENTER_DATA,
    FIRST_HIT,
    DOMAIN,
    FACTORIZED,
    ROOT / "src/bhsm/interface/ae4_current_c2_stop_matched_center_diagnostic.py",
    ROOT / "src/bhsm/interface/aether_cancelled_arc_proper_time_pullback.py",
    ROOT / "src/bhsm/interface/ae4_current_c2_factorized_hs_calderon.py",
    ROOT / "scripts/materialize_ae4_current_c2_stop_matched_center_diagnostic.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


@lru_cache(maxsize=1)
def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    center, first_hit, domain, factorized = (
        _load(path) for path in (CENTER, FIRST_HIT, DOMAIN, FACTORIZED)
    )
    if not all(
        row.get("validation_passed") is True
        for row in (center, first_hit, domain, factorized)
    ):
        raise RuntimeError("validated center, first-hit, domain, and factorization required")
    hit_interval = first_hit["interval_Newton"]["first_hit_action_time_interval"]
    hit_points = {
        "left": float(hit_interval[0]),
        "midpoint": float(first_hit["interval_Newton"]["first_hit_action_time_midpoint"]),
        "right": float(hit_interval[1]),
    }
    with np.load(CENTER_DATA) as source:
        arguments = {
            "arc_nodes": np.asarray(source["collocation_arc_parameters"], dtype=float),
            "states": np.asarray(source["projected_states"], dtype=float),
            "signed_descriptor": np.asarray(
                source["independent_signed_descriptors"], dtype=float
            ),
            "cancelled_field_action_norm": np.asarray(
                source["cancelled_field_action_norm"], dtype=float
            ),
            "cancelled_norm_state_gradient_action": np.asarray(
                source["cancelled_norm_state_gradient_action"], dtype=float
            ),
            "cancelled_norm_descriptor_derivative": np.asarray(
                source["cancelled_norm_descriptor_derivative"], dtype=float
            ),
            "state_weights": np.asarray(source["state_weights"], dtype=float),
        }

    rows: dict[str, Any] = {}
    for hit_label, hit in hit_points.items():
        path = stop_matched_center_proper_time_path(
            **arguments, stop_arc_coordinate=hit,
        )
        refinements: dict[str, Any] = {}
        for refinement in (1, 2, 4, 8):
            x, durations = refine_piecewise_linear_path(
                path["log_radius"], path["proper_times"], refinement,
            )
            channels: dict[str, Any] = {}
            for chirality, label in ((1, "chirality_plus"), (-1, "chirality_minus")):
                channels[label] = factorized_product_dirac_hs_weyl_jet(
                    log_radii=x,
                    proper_durations=durations,
                    dirac_eigenvalue_at_unit_radius=1.5,
                    chirality=chirality,
                    source_profile=np.ones_like(durations),
                    spectral_parameter=-1.0,
                    terminal_load=None,
                    decimal_precision=60,
                )
            refinements[str(refinement)] = {
                "segment_count": int(durations.size),
                "channels": channels,
            }
        rows[hit_label] = {
            "stop_arc_coordinate": hit,
            "proper_duration": path["proper_duration"],
            "history_node_count": int(path["log_radius"].size),
            "birth_log_R4": float(path["log_radius"][0]),
            "terminal_log_R4": float(path["log_radius"][-1]),
            "terminal_descriptor": path["terminal_descriptor"],
            "refinements": refinements,
        }

    midpoint = rows["midpoint"]["refinements"]
    finest = midpoint["8"]["channels"]
    base = midpoint["1"]["channels"]
    convergence = {
        label: {
            key: abs(finest[label][key] - base[label][key])
            for key in ("Weyl_birth_value", "D_H_Weyl_birth", "D2_H_Weyl_birth")
        }
        for label in finest
    }
    hit_spread = {
        label: {
            key: max(
                rows[position]["refinements"]["8"]["channels"][label][key]
                for position in rows
            )
            - min(
                rows[position]["refinements"]["8"]["channels"][label][key]
                for position in rows
            )
            for key in ("Weyl_birth_value", "D_H_Weyl_birth", "D2_H_Weyl_birth")
        }
        for label in finest
    }
    boundary = {
        "AE4_CURRENT_C2_STOP_MATCHED_CENTER_PROPER_TIME_PATH_MATERIALIZED": True,
        "AE4_CURRENT_C2_STOP_MATCHED_CENTER_HS_CALDERON_DIAGNOSTIC_EVALUATED": True,
        "AE4_CURRENT_C2_STOP_MATCHED_NONLINEAR_INTERVAL_PATH_DERIVED": False,
        "AE4_CURRENT_C2_STOP_MOVING_ENDPOINT_HS_JETS_DERIVED": False,
        "AE4_CURRENT_C2_PHYSICAL_STOP_MATCHED_HS_CALDERON_BLOCK_DERIVED": False,
        "AE4_E1_FULL_CORE_HS_HESSIAN_DERIVED": False,
        "PHYSICAL_ENCAPSULATION_IDENTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
    }
    validation = {
        "action_selected_Friedrichs_stop_domain_used": domain["claim_boundary"][
            "AE4_CURRENT_C2_CANONICAL_STOP_FRIEDRICHS_ENDPOINT_SELECTED"
        ],
        "first_hit_left_midpoint_right_all_evaluated": set(rows)
        == {"left", "midpoint", "right"},
        "terminal_descriptor_is_zero": all(
            row["terminal_descriptor"] == 0.0 for row in rows.values()
        ),
        "arc_parameter_not_used_as_proper_time": all(
            1.4e-4 < row["proper_duration"] < 1.6e-4 for row in rows.values()
        ),
        "piecewise_linear_refinement_stable": all(
            result["Weyl_birth_value"] < 1.0e-9
            and result["D_H_Weyl_birth"] < 1.0e-12
            and result["D2_H_Weyl_birth"] < 1.0e-12
            for result in convergence.values()
        ),
        "first_hit_interval_spread_finite": all(
            np.isfinite(value)
            for result in hit_spread.values()
            for value in result.values()
        ),
        "no_finite_terminal_load_inserted": all(
            channel["terminal_Dirichlet_form_core"]
            for row in rows.values()
            for refinement in row["refinements"].values()
            for channel in refinement["channels"].values()
        ),
        "center_diagnostic_not_promoted": not boundary[
            "AE4_CURRENT_C2_PHYSICAL_STOP_MATCHED_HS_CALDERON_BLOCK_DERIVED"
        ],
    }
    return {
        "artifact": "BHSM_AE4_CURRENT_C2_STOP_MATCHED_CENTER_DIAGNOSTIC",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "operator_probe": {
            "spectral_parameter": -1.0,
            "unit_radius_product_Dirac_eigenvalue": 1.5,
            "HS_source_profile": "UNIT_COMMUTING_SUPERPOTENTIAL_SHIFT",
            "terminal_domain": "ACTION_SELECTED_FRIEDRICHS_CANONICAL_STOP",
            "terminal_finite_load": None,
        },
        "stop_interval_center_rows": rows,
        "midpoint_refinement_1_to_8_absolute_change": convergence,
        "certified_first_hit_interval_center_spread_not_outward": hit_spread,
        "scientific_result": {
            "midpoint_finest_chirality_plus": finest["chirality_plus"],
            "midpoint_finest_chirality_minus": finest["chirality_minus"],
            "proper_duration_scale": rows["midpoint"]["proper_duration"],
            "comparison_with_1222_birth_local_core": (
                "THE_STOP_MATCHED_CENTER_HAS_FINITE_DURATION_NEAR_1.477e-4_"
                "AND_A_SECOND_HS_JET_NEAR_9.846e-5;_THE_1.255e-27_PROOF_"
                "PREFIX_IS_NOT_A_PHYSICAL_ENDPOINT_APPROXIMATION"
            ),
        },
        "claim_boundary": boundary,
        "exact_next_calculation": (
            "REPLACE_THE_ACCEPTED_CENTER_DIAGNOSTIC_BY_A_CORRELATION_"
            "PRESERVING_OUTWARD_NONLINEAR_STOP_MATCHED_PATH_AND_ITS_HS_"
            "MOVING_ENDPOINT_JETS,_THEN_REPEAT_THE_SAME_FRIEDRICHS_"
            "FACTORIZED_WEYL_CALCULATION_AS_INTERVAL_AUTHORITY"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("stop-matched center diagnostic validation failed")
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
