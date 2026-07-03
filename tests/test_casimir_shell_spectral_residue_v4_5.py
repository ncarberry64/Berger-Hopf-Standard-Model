import math

import pytest

from bhsm.interface.gauge_coupling_spectral_residue import (
    CASIMIR_SHELL_RESIDUES,
    GAUGE_ADJOINT_DIMS,
    TAU_FRAME_CANDIDATE,
    candidate_lambda_reference,
    candidate_residue_table,
    casimir_shell_residue,
    frame_normalized_residue,
    universal_weyl_3d_density,
)


def test_gauge_dimensions_remain_1_3_8_and_residues_are_not_boson_counts():
    assert GAUGE_ADJOINT_DIMS == {"U1": 1, "SU2": 3, "SU3": 8}
    assert CASIMIR_SHELL_RESIDUES == {"U1": 1, "SU2": 2, "SU3": 7}
    assert [casimir_shell_residue(s) for s in ("U1", "SU2", "SU3")] == [1, 2, 7]
    assert all(row["is_gauge_boson_count"] is False for row in candidate_residue_table().values())


def test_weyl_density_and_reference_lambdas_are_exact_candidates():
    base = 1.0 / (6.0 * math.pi**2)
    assert universal_weyl_3d_density() == base
    assert candidate_lambda_reference("U1") == pytest.approx(0.01688686394038963)
    assert candidate_lambda_reference("SU2") == pytest.approx(0.03377372788077926)
    assert candidate_lambda_reference("SU3") == pytest.approx(0.11820804758272741)


def test_candidate_frame_trace_prevents_three_channel_overcounting():
    assert 3 * TAU_FRAME_CANDIDATE == 1.0
    assert frame_normalized_residue(3, TAU_FRAME_CANDIDATE, 7) == 7.0
