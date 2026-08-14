"""Reproduce the validated v17.31 selection using the parallel Jacobian."""
from __future__ import annotations

import json
import math
from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import (
    PRIORITIES,
    deterministic_json,
    period_priority_family_from,
)
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import (
    RADII,
    v17_30_selected_raw_vector,
)
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import (
    CLASSIFICATION,
    VERSION,
    parallel_sbp_physical_jacobian,
)


def main() -> int:
    result = period_priority_family_from(
        v17_30_selected_raw_vector(),
        source_state="v17.30_selected_event_dense_radius_state",
        priority_owner="v0",
        priority_key="v0_priority",
        selection_key="selected_v0_priority_maximin",
        priorities=PRIORITIES,
        cauchy_factors=RADII,
        jacobian_builder=parallel_sbp_physical_jacobian,
    )
    selected = result["selected_v0_priority_maximin"]
    expected = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_fresh_sbp_third_v0_priority_v17_31.json"
        ).read_text(encoding="utf-8")
    )["fresh_sbp_third_v0_priority"]["selected_v0_priority_maximin"]
    metric_match = all(
        math.isclose(
            selected["metrics"][key], expected["metrics"][key], rel_tol=0, abs_tol=2e-10
        )
        for key in expected["metrics"]
    )
    vector_match = selected["raw_vector_hex"] == expected["raw_vector_hex"]
    validation = {
        "eight_physical_cores_used": result.get("assembly_workers") == 8,
        "same_family": selected["family"] == expected["family"],
        "same_priority": selected["v0_priority"] == expected["v0_priority"],
        "same_radius": selected["cauchy_factor"] == expected["cauchy_factor"],
        "same_exact_metrics": metric_match,
        "same_full_precision_vector": vector_match,
    }
    payload = {
        "artifact": "BHSM_aether_n3_parallel_physical_jacobian_v17_32",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "parallel_equivalence": {
            "source_state": result["source_state"],
            "assembly_workers": result.get("assembly_workers"),
            "column_partition": result.get("column_partition"),
            "selected_v0_priority_maximin": selected,
        },
        "status": "VALIDATED" if all(validation.values()) else "INVALIDATED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    path = Path("artifacts/BHSM_aether_n3_parallel_physical_jacobian_v17_32.json")
    path.write_text(deterministic_json(payload), encoding="utf-8")
    print(path)
    return 0 if payload["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
