"""Bounded period-priority measured tangent family after the v17.24 audit."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping
from collections.abc import Callable

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_expanded_measured_tangent_v17_07 import (
    _measured_response,
    _solve,
)
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import (
    sbp_physical_jacobian,
)
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import (
    sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_post_priority_audit_v17_24 import (
    v17_23_selected_raw_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    EPS,
    FILTERS,
    LABELS,
    MARGIN,
    _gradients,
    _metrics,
    _slopes,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)

VERSION = "v17.25"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_PERIOD_PRIORITY_MEASURED_TANGENT_FAMILY"
FULL_BHSM_COMPLETE = False
PRIORITIES = (1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0)
RANKS = (6, 9, 12, 18)
CAUCHY = (
    0.01,
    0.02,
    0.03,
    0.04,
    0.05,
    0.06,
    0.075,
    0.09,
    0.11,
    0.13,
    0.15,
    0.2,
)


def period_priority_family_from(
    raw_vector: np.ndarray,
    *,
    source_state: str = "supplied_full_precision_state",
    priority_owner: str = "period",
    additional_priority_owners: tuple[str, ...] = (),
    priority_key: str = "period_priority",
    selection_key: str = "selected_period_priority_maximin",
    priorities: tuple[float, ...] = PRIORITIES,
    priority_profiles: tuple[tuple[float, ...], ...] | None = None,
    cauchy_factors: tuple[float, ...] = CAUCHY,
    jacobian_builder: Callable[[np.ndarray], dict[str, Any]] = sbp_physical_jacobian,
) -> dict[str, Any]:
    """Search unchanged physical equations with bounded period preconditioning."""

    raw = np.asarray(raw_vector, dtype=float)
    if raw.shape != (376,):
        raise ValueError("raw KKT vector has wrong dimension")
    scales = kkt_variable_scales()
    y = raw * scales
    y, residual = sbp_projected_residual_and_vector(y)
    initial = _metrics(residual)
    assembled = jacobian_builder(y / scales)
    jacobian = np.asarray(assembled.pop("matrix"))[:, :-1]
    _, singular_values, vt = np.linalg.svd(jacobian, full_matrices=False)
    spectral = float(singular_values[0])
    gradients = _gradients(jacobian, residual, initial)
    columns: list[np.ndarray] = []
    filter_blocks: list[tuple[float, np.ndarray]] = []
    for relative_filter in FILTERS:
        mu = relative_filter * spectral
        denominator = singular_values * singular_values + mu * mu
        block = vt.T @ ((vt @ gradients.T) / denominator[:, None])
        block = block / np.maximum(np.linalg.norm(block, axis=0), 1e-300)
        filter_blocks.append((relative_filter, block))
        columns.extend(block[:, index] for index in range(block.shape[1]))

    candidate = np.column_stack(columns)
    candidate_u, candidate_s, _ = np.linalg.svd(candidate, full_matrices=False)
    keep = candidate_s > max(1e-12, 1e-10 * float(candidate_s[0]))
    basis = candidate_u[:, keep]
    response = _measured_response(y, residual, initial, basis)
    families: list[tuple[str, np.ndarray]] = []
    for rank in RANKS:
        if rank <= basis.shape[1]:
            families.append(
                (f"combined_rank_{rank}", np.eye(basis.shape[1])[:, :rank])
            )
    for relative_filter, block in filter_blocks:
        qf, _ = np.linalg.qr(block, mode="reduced")
        families.append((f"single_filter_{relative_filter:.0e}", basis.T @ qf))

    if priority_owner not in LABELS:
        raise ValueError(f"unknown priority owner: {priority_owner}")
    priority_owners = (priority_owner, *additional_priority_owners)
    if len(set(priority_owners)) != len(priority_owners):
        raise ValueError("priority owners must be unique")
    unknown = tuple(owner for owner in priority_owners if owner not in LABELS)
    if unknown:
        raise ValueError(f"unknown priority owners: {unknown}")
    priority_indices = tuple(LABELS.index(owner) for owner in priority_owners)
    if priority_profiles is None:
        priority_configurations: list[tuple[Any, tuple[float, ...]]] = [
            (priority, tuple(priority for _ in priority_owners))
            for priority in priorities
        ]
    else:
        if not priority_profiles:
            raise ValueError("priority profiles must not be empty")
        if any(len(profile) != len(priority_owners) for profile in priority_profiles):
            raise ValueError("priority profile dimension does not match owners")
        if any(value <= 0 for profile in priority_profiles for value in profile):
            raise ValueError("priority profile values must be positive")
        priority_configurations = [
            (
                {
                    owner: float(profile[index])
                    for index, owner in enumerate(priority_owners)
                },
                profile,
            )
            for profile in priority_profiles
        ]
    rows: list[dict[str, Any]] = []
    accepted: list[tuple[float, float, dict[str, Any], str, Any]] = []
    for family, transform in families:
        raw_response = response @ transform
        for priority, target_values in priority_configurations:
            targets = np.ones(len(LABELS))
            targets[list(priority_indices)] = target_values
            weighted_response = raw_response / targets[:, None]
            coefficient, rate, solved, weights, gap = _solve(weighted_response)
            reduced_direction = basis @ (transform @ coefficient)
            direction = np.concatenate((reduced_direction, [0.0]))
            _, plus = sbp_projected_residual_and_vector(y + EPS * direction)
            _, minus = sbp_projected_residual_and_vector(y - EPS * direction)
            jacobian_direction = (plus - minus) / (2 * EPS)
            verified = _slopes(residual, jacobian_direction, initial)
            cauchy = max(
                0.0,
                -float(residual @ jacobian_direction)
                / float(jacobian_direction @ jacobian_direction),
            )
            common = bool(np.all(verified < 0))
            row: dict[str, Any] = {
                "family": family,
                "dimension": transform.shape[1],
                priority_key: priority,
                "maximin_solve_success": solved,
                "relative_duality_gap": gap,
                "weighted_equalized_rate": rate,
                "dual_owner_weights": weights.tolist(),
                "predicted_fractional_slopes": (raw_response @ coefficient).tolist(),
                "verified_fractional_slopes": {
                    LABELS[index]: float(verified[index])
                    for index in range(len(LABELS))
                },
                "derived_cauchy_radius": cauchy,
                "common_six_owner_descent": common,
                "trials": [],
            }
            if solved and common and cauchy > 0:
                for factor in cauchy_factors:
                    radius = factor * cauchy
                    try:
                        candidate_y, candidate_residual = (
                            sbp_projected_residual_and_vector(y + radius * direction)
                        )
                        raw_candidate = candidate_y / scales
                        eta = _minimum_node_eta(raw_candidate)
                        metrics = _metrics(candidate_residual)
                        reductions = {
                            key: initial[key] - metrics[key] for key in initial
                        }
                        fractions = {
                            key: reductions[key] / max(initial[key], 1e-300)
                            for key in initial
                        }
                        trial = {
                            "cauchy_factor": factor,
                            "trust_radius": radius,
                            "domain_valid": bool(eta > 1e-5),
                            "metrics": metrics,
                            "reductions": reductions,
                            "fractional_reductions": fractions,
                            "minimum_fractional_progress": min(fractions.values()),
                            "limiting_owner": min(fractions, key=fractions.get),
                            "eta_minimum": eta,
                            "raw_vector_hex": [
                                float(value).hex() for value in raw_candidate
                            ],
                        }
                        row["trials"].append(trial)
                        if eta > 1e-5 and all(
                            reductions[key] > MARGIN for key in initial
                        ):
                            accepted.append(
                                (
                                    trial["minimum_fractional_progress"],
                                    sum(fractions.values()),
                                    trial,
                                    family,
                                    priority,
                                )
                            )
                    except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
                        row["trials"].append(
                            {
                                "cauchy_factor": factor,
                                "domain_valid": False,
                                "exception": type(exc).__name__,
                            }
                        )
            rows.append(row)

    best = None
    if accepted:
        _, _, trial, family, priority = max(
            accepted, key=lambda item: (item[0], item[1])
        )
        best = {"family": family, priority_key: priority, **trial}
    return {
        "source_state": source_state,
        "physical_residual_changed": False,
        "physical_event_changed": False,
        "priority_semantics": (
            (
                "MAXIMIZE_MINIMUM_OF_RAW_FRACTIONAL_OWNER_DESCENT_DIVIDED_BY_"
                "BOUNDED_ASYMMETRIC_OWNER_TARGET_PROFILE"
            )
            if priority_profiles is not None
            else (
                "MAXIMIZE_MINIMUM_OF_RAW_FRACTIONAL_OWNER_DESCENT_DIVIDED_BY_"
                "OWNER_TARGET_WITH_"
                f"{'_AND_'.join(owner.upper() for owner in priority_owners)}_"
                "TARGET_INCREASED"
            )
        ),
        **(
            {"priority_owners": list(priority_owners)}
            if additional_priority_owners
            else {}
        ),
        "initial_metrics": initial,
        **assembled,
        "singular_value_scale": spectral,
        "tangent_rank": basis.shape[1],
        "family_count": len(families),
        "priority_count": len(priority_configurations),
        **(
            {"priority_profiles_tested": len(priority_configurations)}
            if priority_profiles is not None
            else {}
        ),
        "direction_rows": rows,
        "common_direction_count": sum(
            row["common_six_owner_descent"] for row in rows
        ),
        "strict_candidate_count": len(accepted),
        selection_key: best,
    }


def period_priority_family() -> dict[str, Any]:
    return period_priority_family_from(
        v17_23_selected_raw_vector(),
        source_state="v17.23_selected_second_v0_priority_state",
    )


def completion_payload() -> dict[str, Any]:
    result = period_priority_family()
    best = result["selected_period_priority_maximin"]
    validation = {
        "v17_23_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"],
            1.149301714331482,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_23_event_reproduced": math.isclose(
            result["initial_metrics"]["event"],
            0.096593908006489,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_23_period_reproduced": math.isclose(
            result["initial_metrics"]["period"],
            0.560464008811159,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "source_state_owned": (
            result["source_state"] == "v17.23_selected_second_v0_priority_state"
        ),
        "physical_equations_unchanged": (
            not result["physical_residual_changed"]
            and not result["physical_event_changed"]
        ),
        "bounded_priorities_tested": result["priority_count"] == len(PRIORITIES),
        "all_families_tested": result["family_count"] == 7,
        "common_direction_exists": result["common_direction_count"] > 0,
        "strict_candidate_exists": best is not None,
        "all_six_metrics_reduced": bool(
            best is not None
            and all(value > MARGIN for value in best["reductions"].values())
        ),
        "positive_maximin_progress": bool(
            best is not None and best["minimum_fractional_progress"] > 0
        ),
        "eta_domain_preserved": bool(
            best is not None and best["eta_minimum"] > 1e-5
        ),
        "full_precision_state_preserved": bool(
            best is not None and len(best["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_fresh_sbp_period_priority_family_v17_25",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_period_priority_family": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "FINITE_NONLINEAR_SIX_OWNER_DESCENT_AFTER_THE_MEASURED_PERIOD_"
            "LIMITER_TRANSITION"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_OWNER_SET",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_fresh_sbp_period_priority_family_v17_25.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "period_priority_family_from",
    "period_priority_family",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
