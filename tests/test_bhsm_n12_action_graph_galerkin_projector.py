from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "artifacts/n12_continuum_majorant_effectiveness"
    / "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)


def test_action_graph_projector_correction_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["M_star_certified"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["reclassification"][
        "previous_comparison_of_weighted_principal_gap_with_raw_"
        "frequency_tail_is_a_common_norm_certificate"
    ] is False
    assert payload["weighted_L2_Jacobi_Fortin_tail_closed"] is True
    assert payload["full_normal_compact_tail_closed"] is False

    rows = payload["analytic_countersequence"]["rows"]
    norms = [row["canonical_omega_graph_norm"] for row in rows]
    assert all(left > right for left, right in zip(norms, norms[1:]))
    assert all(row["raw_b0_after_normalization"] == 1.0 for row in rows)
    assert 0.5 < rows[-1]["K_times_graph_norm"] < 0.75

    shape = payload["finite_diagnostics"]["shape_b"]
    assert shape[-1][
        "raw_coefficient_low_projection_norm_in_natural_graph"
    ] > shape[0]["raw_coefficient_low_projection_norm_in_natural_graph"]
    assert all(
        abs(row["action_orthogonal_projection_norm_in_natural_graph"] - 1.0)
        < 2.0e-8
        for family in payload["finite_diagnostics"].values()
        for row in family
    )

    for side in payload["trace_compatible_galerkin_decomposition"][
        "finite_roundoff_diagnostics"
    ].values():
        assert all(row["attachment_trace_tail_defect"] < 2.0e-9 for row in side)
        assert all(
            abs(row["trace_kernel_action_orthogonal_projection_norm"] - 1.0)
            < 2.0e-8
            for row in side
        )

    fortin = payload["explicit_weighted_Jacobi_Fortin_tail"]["rows"]
    assert all(
        left["scale_fixed_u_G_to_weighted_L2_tail_upper"]
        > right["scale_fixed_u_G_to_weighted_L2_tail_upper"]
        and left[
            "existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper"
        ] > right[
            "existing_scale_core_augmented_u_G_to_weighted_L2_tail_upper"
        ]
        and left["windowed_shape_G_to_weighted_L2_tail_upper"]
        > right["windowed_shape_G_to_weighted_L2_tail_upper"]
        for left, right in zip(fortin, fortin[1:])
    )
    assert fortin[0]["M"] == 12
    assert fortin[0]["windowed_shape_G_to_weighted_L2_tail_upper"] < 1.0
