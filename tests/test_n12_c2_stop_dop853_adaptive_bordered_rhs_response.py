"""Checks for the adaptive, action-owned DOP853 bordered response tube."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
LOCALIZATION = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE.json"
CERTIFICATE = BASE / "BHSM_N12_C2_STOP_DOP853_ADAPTIVE_BORDERED_RHS_RESPONSE_CERTIFICATE.json"
sys.path.insert(0, str(ROOT / "scripts"))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_four_child_localization_is_diagnostic_not_promoted() -> None:
    payload = load(LOCALIZATION)
    assert payload["mesh"] == {
        "adaptive_parent_cells": 1722,
        "response_cells": 6888,
        "response_refinement_per_parent": 4,
        "workers": payload["mesh"]["workers"],
    }
    assert all(row["selected_branch"] == 24 for row in payload["rows"])
    assert all(row["center_internal_rhs_finite"] for row in payload["rows"])
    assert payload["source_ontology"].startswith(
        "EXTERNAL_CAUCHY_BIRTH_SOURCE_ZERO"
    )


def test_refined_response_cover_is_exact_and_finite() -> None:
    payload = load(CERTIFICATE)
    rows = payload["rows"]
    assert payload["validation_passed"] is True
    assert payload["unresolved_cells"] == []
    assert payload["mesh"]["four_child_localization_cells"] == 6888
    assert payload["mesh"]["localization_failed_cells"] > 0
    assert payload["validation"][
        "failed_response_cells_replaced_only_by_exact_dyadic_children"
    ] is True
    assert payload["claim_boundary"][
        "bordered_hard_response_on_stored_DOP853_stop_path"
    ] == "CERTIFIED_FINITE"
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(row["relative_bordered_operator_perturbation_upper"] < 1.0 for row in rows)
    assert all(math.isfinite(row["complete_bordered_response_2_norm_upper"]) for row in rows)
    assert all(
        math.isfinite(row["raw_internal_rhs_first_coefficient_derivative_2_norm_upper"])
        and math.isfinite(row["raw_internal_rhs_second_coefficient_derivative_2_norm_upper"])
        for row in rows
    )

    grouped: dict[int, list[tuple[Fraction, Fraction]]] = defaultdict(list)
    for row in rows:
        numerator = int(row["subspan"])
        denominator = int(row["subdivisions"])
        grouped[int(row["interval"])].append((
            Fraction(numerator, denominator),
            Fraction(numerator + 1, denominator),
        ))
    assert set(grouped) == set(range(370))
    for spans in grouped.values():
        spans.sort()
        assert spans[0][0] == 0
        assert spans[-1][1] == 1
        assert all(left[1] == right[0] for left, right in zip(spans, spans[1:]))


def test_tangent_remainder_ellipsoid_contains_exact_degree_seven_cell() -> None:
    import certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response as response
    import derive_n12_action_ball_majorants as majorants

    assert majorants.BALL_RADIUS == 1.0

    geometry = response._tight_tangent_remainder_geometry(0, 0, 32)
    *_, weights, __, ___, ____ = response.dense._dense_arrays()
    center_action = geometry["midpoint"] * weights
    projection = geometry["projection"]
    controls = geometry["Bezier_controls"]
    assert abs(geometry["coefficient_ellipsoid_identity"] - 1.0) <= 4.0e-15
    for u in np.linspace(0.0, 1.0, 33):
        point = sum(
            math.comb(7, index) * u**index * (1.0 - u) ** (7 - index)
            * controls[index]
            for index in range(8)
        )
        delta = point - center_action
        coefficients, *_ = np.linalg.lstsq(projection, delta, rcond=None)
        assert np.linalg.norm(projection @ coefficients - delta) <= 1.0e-12
        assert np.linalg.norm(coefficients) <= 1.0 + 2.0e-10


def test_response_certificate_input_hashes_match_disk() -> None:
    payload = load(CERTIFICATE)
    for relative, expected in payload["inputs"].items():
        assert normalized_sha256(ROOT / relative) == expected
    assert payload["validation"]["only_external_Cauchy_birth_source_zero_internal_rhs_retained"] is True
    assert payload["validation"]["no_added_seam_force_or_double_counted_response"] is True
    assert payload["validation"]["no_full_kinetic_Dirac_or_history_inverse_used"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["FLAGSHIP_READY"] is False
