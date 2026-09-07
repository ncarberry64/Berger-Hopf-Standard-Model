"""Materialize the exact selected-area seam selection audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.covariant_interface_seam_selection import build_payload  # noqa: E402


RESULT = ROOT / "artifacts/action_extension/BHSM_COVARIANT_INTERFACE_SEAM_SELECTION_AUDIT.json"
INPUTS = (
    "theory/bhsm_owner_authorized_encapsulation_interface_action.md",
    "theory/bhsm_covariant_bubble_interface_mechanics.md",
    "src/bhsm/interface/covariant_bubble_interface_mechanics.py",
    "theory/bhsm_covariant_interface_seam_selection_audit.md",
    "src/bhsm/interface/covariant_interface_seam_selection.py",
    "scripts/materialize_covariant_interface_seam_selection.py",
    "tests/test_covariant_interface_seam_selection.py",
)


def materialize() -> dict[str, object]:
    payload = build_payload()
    payload["inputs"] = {
        name: hashlib.sha256(
            (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest().upper()
        for name in INPUTS
    }
    cases = payload["rank_cases"]
    graph = payload["conditional_Lagrangian_graph"]
    payload["validation"] = {
        "zero_field_rank_zero": cases["zero_traces"]["exact_rank"] == 0,
        "curvature_only_leaves_kernel": cases["curvature_only"]["kernel_dimension"] == 1,
        "aligned_stationary_case_leaves_kernel": (
            cases["aligned_nonzero_flux"]["exact_rank"] == 2
            and cases["aligned_nonzero_flux"]["isolated_Maxwell_free_map_stationary"]
        ),
        "independent_flux_rank_three_but_isolated_stationarity_fails": (
            cases["independent_nonzero_flux"]["exact_rank"] == 3
            and not cases["independent_nonzero_flux"]["isolated_Maxwell_free_map_stationary"]
        ),
        "conditional_graph_has_half_dimension_and_zero_Green_form": (
            2 * graph["graph_dimension"] == graph["product_dimension"]
            and all(entry == "0" for row in graph["restricted_Green_form"] for entry in row)
        ),
        "nonidentity_reference_preserves_metric_but_changes_flux": (
            payload["nonidentity_reference_check"]["preserves_metric"]
            and any(
                entry != "0"
                for row in payload["nonidentity_reference_check"]["identity_flux_residual_against_reference"]
                for entry in row
            )
        ),
        "no_physical_reset_or_rank_promotion": (
            not graph["physical_L_s_selected"]
            and payload["N12"]["new_independent_rank"] == 0
            and not payload["N12"]["Gate7_result_imported"]
            and not payload["FULL_BHSM_COMPLETE"]
        ),
    }
    payload["validation_passed"] = all(payload["validation"].values())
    return payload


def main() -> None:
    payload = materialize()
    if not payload["validation_passed"]:
        raise SystemExit("seam-selection audit validation failed")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": payload["status"],
        "validation_passed": payload["validation_passed"],
        "physical_F_B_selected": False,
        "new_N12_rank": payload["N12"]["new_independent_rank"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
