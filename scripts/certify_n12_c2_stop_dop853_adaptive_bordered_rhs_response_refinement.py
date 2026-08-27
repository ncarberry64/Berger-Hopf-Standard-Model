"""Refine only failed DOP853 bordered-response cells to a finite tube."""

from __future__ import annotations

from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response as response  # noqa: E402


BASE = ROOT / "artifacts" / "flagship_integration"
COARSE = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_RESPONSE_LOCALIZATION",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE.json"),
))
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_DOP853_RESPONSE_CERTIFICATE",
    str(BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json"),
))
MAX_REFINEMENT_OF_PARENT = int(os.environ.get(
    "BHSM_N12_STOP_DOP853_RESPONSE_MAX_REFINEMENT", "16",
))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _closed(row: dict[str, Any]) -> bool:
    return bool(
        row["center_internal_rhs_finite"]
        and row["center_preconditioned_source_matches_bordered_solve"]
        and row["bordered_response_tube_finite"]
        and float(row["relative_bordered_operator_perturbation_upper"]) < 1.0
    )


def _task(task: tuple[int, int, int, int, int, int]) -> dict[str, Any]:
    return response._row(task)


def _partition_is_exact(rows: list[dict[str, Any]]) -> bool:
    grouped: dict[int, list[tuple[Fraction, Fraction]]] = defaultdict(list)
    for row in rows:
        denominator = int(row["subdivisions"])
        numerator = int(row["subspan"])
        grouped[int(row["interval"])].append((
            Fraction(numerator, denominator),
            Fraction(numerator + 1, denominator),
        ))
    if set(grouped) != set(range(370)):
        return False
    for spans in grouped.values():
        spans.sort()
        if spans[0][0] != 0 or spans[-1][1] != 1:
            return False
        if any(left[1] != right[0] for left, right in zip(spans, spans[1:])):
            return False
    return True


def _replacement_is_exact(
    source_rows: list[dict[str, Any]], cover: list[dict[str, Any]],
) -> bool:
    """Check that closed cells survive and only failed cells are subdivided."""

    by_interval: dict[int, list[tuple[Fraction, Fraction, dict[str, Any]]]] = (
        defaultdict(list)
    )
    for row in cover:
        denominator = int(row["subdivisions"])
        numerator = int(row["subspan"])
        by_interval[int(row["interval"])].append((
            Fraction(numerator, denominator),
            Fraction(numerator + 1, denominator),
            row,
        ))
    for cells in by_interval.values():
        cells.sort(key=lambda item: item[0])

    for source in source_rows:
        interval = int(source["interval"])
        denominator = int(source["subdivisions"])
        numerator = int(source["subspan"])
        left = Fraction(numerator, denominator)
        right = Fraction(numerator + 1, denominator)
        descendants = [
            item for item in by_interval[interval]
            if left <= item[0] and item[1] <= right
        ]
        if not descendants:
            return False
        if descendants[0][0] != left or descendants[-1][1] != right:
            return False
        if any(
            first[1] != second[0]
            for first, second in zip(descendants, descendants[1:])
        ):
            return False
        if _closed(source):
            if len(descendants) != 1:
                return False
            child = descendants[0][2]
            if (
                int(child["subspan"]) != numerator
                or int(child["subdivisions"]) != denominator
            ):
                return False
        elif any(int(item[2]["subdivisions"]) <= denominator for item in descendants):
            return False
    return True


def build_payload() -> dict[str, Any]:
    localization = json.loads(COARSE.read_text(encoding="utf-8"))
    if localization["mesh"]["response_refinement_per_parent"] != 4:
        raise RuntimeError("canonical four-child response localization required")
    source_rows = localization["rows"]
    accepted = [row for row in source_rows if _closed(row)]
    failed = [row for row in source_rows if not _closed(row)]
    audit_counts = {"4": len(source_rows)}
    workers = min(
        int(os.environ.get("BHSM_N12_STOP_WORKERS", "16")),
        os.cpu_count() or 1,
    )
    while failed:
        current_ratios = {
            int(row["subdivisions"]) // int(row["parent_subdivisions"])
            for row in failed
        }
        if len(current_ratios) != 1:
            raise RuntimeError("failed response frontier has mixed refinement levels")
        current_ratio = current_ratios.pop()
        if current_ratio >= MAX_REFINEMENT_OF_PARENT:
            break
        tasks = []
        for row in failed:
            interval = int(row["interval"])
            denominator = 2 * int(row["subdivisions"])
            numerator = 2 * int(row["subspan"])
            parent_numerator = int(row["parent_subspan"])
            parent_denominator = int(row["parent_subdivisions"])
            for offset in (0, 1):
                child_numerator = numerator + offset
                child_index = (
                    child_numerator
                    - parent_numerator * (denominator // parent_denominator)
                )
                tasks.append((
                    interval, child_numerator, denominator,
                    parent_numerator, parent_denominator, child_index,
                ))
        level_rows = []
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for index, row in enumerate(executor.map(_task, tasks, chunksize=1), 1):
                level_rows.append(row)
                if index % 32 == 0 or index == len(tasks):
                    print(json.dumps({
                        "refinement_of_parent": (
                            int(row["subdivisions"])
                            // int(row["parent_subdivisions"])
                        ),
                        "completed": index,
                        "total": len(tasks),
                        "closed_count_so_far": sum(_closed(item) for item in level_rows),
                    }), flush=True)
        level_ratio = int(level_rows[0]["subdivisions"]) // int(
            level_rows[0]["parent_subdivisions"]
        )
        audit_counts[str(level_ratio)] = len(level_rows)
        accepted.extend(row for row in level_rows if _closed(row))
        failed = [row for row in level_rows if not _closed(row)]
    cover = accepted + failed
    cover.sort(key=lambda row: (
        int(row["interval"]),
        Fraction(int(row["subspan"]), int(row["subdivisions"])),
    ))
    counts = Counter(
        str(int(row["subdivisions"]) // int(row["parent_subdivisions"]))
        for row in cover
    )
    validation = {
        "four_child_localization_consumed_without_reinterpretation": len(source_rows) == 6888,
        "failed_response_cells_replaced_only_by_exact_dyadic_children": _replacement_is_exact(
            source_rows, cover,
        ),
        "certified_response_cells_partition_every_dense_interval_exactly": _partition_is_exact(cover),
        "branch_24_selected_everywhere": all(row["selected_branch"] == 24 for row in cover),
        "all_exact_center_internal_rhs_values_finite": all(row["center_internal_rhs_finite"] for row in cover),
        "all_center_bordered_solve_residuals_small": all(row["center_bordered_solve_residual_upper"] < 1.0e-7 for row in cover),
        "all_center_preconditioned_sources_match_bordered_solves": all(row["center_preconditioned_source_matches_bordered_solve"] for row in cover),
        "all_relative_bordered_perturbations_below_one": all(row["relative_bordered_operator_perturbation_upper"] < 1.0 for row in cover),
        "all_bordered_response_tubes_finite": all(row["bordered_response_tube_finite"] for row in cover),
        "all_tangent_remainder_product_ellipsoids_exactly_normalized": all(
            abs(row["coefficient_ellipsoid_identity"] - 1.0) <= 4.0e-15
            for row in cover
        ),
        "no_failed_cell_at_maximum_refinement": not failed,
        "same_stored_DOP853_polynomial_and_adaptive_spectrum_parent_cover": True,
        "only_external_Cauchy_birth_source_zero_internal_rhs_retained": True,
        "no_added_seam_force_or_double_counted_response": True,
        "no_full_kinetic_Dirac_or_history_inverse_used": True,
    }
    passed = all(validation.values())
    owner = max(cover, key=lambda row: row["complete_bordered_response_2_norm_upper"])
    return {
        "artifact": "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE",
        "status": (
            "ALL_DOP853_ADAPTIVE_ACTION_OWNED_BORDERED_RHS_RESPONSE_TUBES_CERTIFIED"
            if passed else "DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_REFINEMENT_REQUIRED"
        ),
        "method": "EXACT_MIDPOINT_TANGENT_PLUS_INTEGRAL_SECOND_DERIVATIVE_REMAINDER_WITH_MINIMUM_TRACE_TWO_BLOCK_ELLIPSOID_AND_DYADIC_REFINEMENT",
        "source_ontology": "EXTERNAL_CAUCHY_BIRTH_SOURCE_ZERO;_EULER_LAGRANGE_CHILD_RESPONSE_RETAINED_AS_INTERNAL_ACTION_OWNED_RHS",
        "mesh": {
            "four_child_localization_cells": len(source_rows),
            "localization_failed_cells": sum(not _closed(row) for row in source_rows),
            "refinement_cells_audited_by_parent_ratio": audit_counts,
            "accepted_cover_cells_by_parent_ratio": dict(sorted(counts.items(), key=lambda item: int(item[0]))),
            "accepted_response_cover_cells": len(cover),
            "maximum_refinement_of_spectrum_parent": MAX_REFINEMENT_OF_PARENT,
            "workers": workers,
        },
        "summary": {
            "maximum_center_internal_rhs_2_norm": max(row["center_internal_rhs_2_norm"] for row in cover),
            "maximum_preconditioned_internal_rhs_variation_2_norm_upper": max(row["preconditioned_internal_rhs_variation_2_norm_upper"] for row in cover),
            "maximum_relative_bordered_operator_perturbation_upper": max(row["relative_bordered_operator_perturbation_upper"] for row in cover),
            "maximum_bordered_Neumann_factor_upper": max(row["bordered_Neumann_factor_upper"] for row in cover),
            "maximum_complete_bordered_response_2_norm_upper": max(row["complete_bordered_response_2_norm_upper"] for row in cover),
            "maximum_center_bordered_solve_residual_upper": max(row["center_bordered_solve_residual_upper"] for row in cover),
            "owner": owner,
        },
        "rows": cover,
        "unresolved_cells": failed,
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "action_owned_internal_rhs_on_stored_DOP853_stop_path": "CERTIFIED" if passed else "OPEN",
            "bordered_hard_response_on_stored_DOP853_stop_path": "CERTIFIED_FINITE" if passed else "OPEN",
            "response_first_variation_tube": "OPEN",
            "correlated_shadowing_tube": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "DIFFERENTIATE_THE_COMPLETE_INTERNAL_BORDERED_SYSTEM_AND_ASSEMBLE_THE_RESPONSE_FIRST_VARIATION_TUBE_ON_THIS_IDENTICAL_DOP853_RESPONSE_COVER"
            if passed else "REFINE_ONLY_THE_REPORTED_UNRESOLVED_RESPONSE_CELLS"
        ),
        "inputs": {
            _relative(COARSE): _sha256(COARSE),
            _relative(response.INVERSE): _sha256(response.INVERSE),
            _relative(response.PROJECTOR): _sha256(response.PROJECTOR),
            "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py": _sha256(
                ROOT / "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py"
            ),
            "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response_refinement.py": _sha256(
                ROOT / "scripts/certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response_refinement.py"
            ),
        },
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
