"""Compare a direct v20.99 curvature refresh against failed secant transport."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import dual_metric_range_space_proposal
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_99 import v20_99_selected_raw_vector


VERSION = "v21.02"
CLASSIFICATION = "BHSM_N3_DIRECT_REFRESH_VS_CURVATURE_TRANSPORT_PROPOSAL"
FULL_BHSM_COMPLETE = False


def _nested(path: str, key: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))[key]


def completion_payload() -> dict[str, Any]:
    result = dual_metric_range_space_proposal(
        v20_99_selected_raw_vector(),
        source_label="v20.99",
        curvature_artifact="artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V21_01.json",
        curvature_key="curvature_singular_subspace_refresh",
    )
    transported = _nested(
        "artifacts/BHSM_N3_CURVATURE_TRANSPORT_PROPOSAL_V21_00.json",
        "curvature_transport_proposal",
    )
    audit_92 = _nested(
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_93.json",
        "curvature_singular_subspace_refresh",
    )
    audit_95 = _nested(
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_97.json",
        "curvature_singular_subspace_refresh",
    )
    audit_99 = _nested(
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V21_01.json",
        "curvature_singular_subspace_refresh",
    )
    transport_meta = json.loads(Path(
        "artifacts/BHSM_N3_CURVATURE_TRANSPORT_PROPOSAL_V21_00.json"
    ).read_text(encoding="utf-8"))["curvature_transport"]
    block_92 = np.asarray(audit_92["event_curvature_symmetric_block"], dtype=float)
    block_95 = np.asarray(audit_95["event_curvature_symmetric_block"], dtype=float)
    block_99 = np.asarray(audit_99["event_curvature_symmetric_block"], dtype=float)
    ratio = float(transport_meta["physical_secant_arc_ratio"])
    block_transport = block_95 + ratio * (block_95 - block_92)
    transport_best = transported["exact_search"]["best"]
    direct_best = result["exact_search"]["best"]
    comparison = {
        "transport_block_relative_error_vs_direct_refresh": float(
            np.linalg.norm(block_transport - block_99) / np.linalg.norm(block_99)
        ),
        "direct_block_relative_change_from_v20_95": float(
            np.linalg.norm(block_99 - block_95) / np.linalg.norm(block_95)
        ),
        "transport_exact_reduction": None if transport_best is None else transport_best["exact_reduction"],
        "direct_refresh_exact_reduction": None if direct_best is None else direct_best["exact_reduction"],
        "transport_promoted": transported["promotion"]["promoted"],
        "direct_refresh_promoted": result["promotion"]["promoted"],
        "classification": "CURVATURE_SECANT_TRANSPORT_INVALIDATED" if (
            direct_best is not None
            and transport_best is not None
            and direct_best["exact_reduction"] > 10.0 * transport_best["exact_reduction"]
        ) else "CURVATURE_TRANSPORT_NOT_DECISIVELY_SEPARATED",
    }
    validation = {
        "source_v20_99_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.782780987846174
        ) < 5.0e-12,
        "v21_01_direct_curvature_used": result["dual_metric_model"]["curvature_artifact"].endswith("V21_01.json"),
        "transport_was_prospective": not transport_meta["future_curvature_used_to_construct"],
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": direct_best is None or direct_best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_DIRECT_REFRESH_PROPOSAL_V21_02",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "direct_refresh_proposal": result,
        "transport_validation": comparison,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_DIRECT_REFRESH_PROPOSAL_V21_02.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
