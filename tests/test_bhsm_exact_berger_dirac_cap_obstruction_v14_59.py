from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import (
    EXACT_NEXT_OBJECT,
    BergerParameters,
    CapParameters,
    FROZEN_BERGER_STRETCH,
    artifact_payloads,
    berger_dirac_block,
    berger_dirac_derivative_block,
    berger_u1_obstruction_payload,
    berger_zero_mode_payload,
    cap_first_variation,
    cap_nonuniqueness_payload,
    completion_gate_payload,
    exact_berger_operator_payload,
    fiber_u1_generator,
    homogeneous_dirac_block,
    low_berger_spectrum,
    materialize,
    n1_berger_exact_eigenvalues,
    partial_projector_payload,
    physical_readiness_payload,
    projector_residuals,
    round_block_expected_eigenvalues,
    spectral_nonzero_projector,
    spin_matrices,
    validate_berger,
    validate_cap,
)


def test_spin_commutation_relations() -> None:
    jx, jy, jz = spin_matrices(5)
    assert np.linalg.norm(jx @ jy - jy @ jx - 1j * jz) < 1e-12
    assert np.linalg.norm(jy @ jz - jz @ jy - 1j * jx) < 1e-12
    assert np.linalg.norm(jz @ jx - jx @ jz - 1j * jy) < 1e-12


def test_homogeneous_block_is_hermitian() -> None:
    block = homogeneous_dirac_block(4, 1.2, 0.9, 0.7)
    assert np.linalg.norm(block - block.conjugate().T) < 1e-12


@pytest.mark.parametrize("n", range(8))
def test_round_spectrum_recovered_blockwise(n: int) -> None:
    radius = 1.7
    computed = np.linalg.eigvalsh(berger_dirac_block(n, radius, 1.0))
    expected = np.array(round_block_expected_eigenvalues(n, radius))
    assert computed == pytest.approx(expected, abs=1e-12)


def test_exact_n1_berger_formula() -> None:
    radius = 1.3
    stretch = 2.7
    computed = np.linalg.eigvalsh(berger_dirac_block(1, radius, stretch))
    assert computed == pytest.approx(n1_berger_exact_eigenvalues(radius, stretch), abs=1e-12)


def test_first_zero_mode_at_stretch_four() -> None:
    payload = berger_zero_mode_payload()
    assert payload["critical_internal_kernel_dimension"] == 1
    assert payload["critical_full_isotypical_kernel_multiplicity"] == 2
    assert min(abs(value) for value in payload["critical_n1_numeric_eigenvalues"]) < 1e-12


def test_frozen_berger_block_is_gapped() -> None:
    payload = berger_zero_mode_payload()
    assert payload["frozen_stretch"] == pytest.approx(FROZEN_BERGER_STRETCH)
    assert payload["frozen_internal_kernel_dimension"] == 0
    assert payload["frozen_gap"] > 1.0


def test_analytic_berger_derivative_matches_finite_difference() -> None:
    n = 4
    radius = 1.2
    stretch = 1.37
    delta = 1e-6
    numerical = (
        berger_dirac_block(n, radius, stretch + delta)
        - berger_dirac_block(n, radius, stretch - delta)
    ) / (2.0 * delta)
    analytic = berger_dirac_derivative_block(n, radius, stretch)
    assert np.linalg.norm(numerical - analytic) < 1e-8


def test_time_dependent_berger_blocks_noncommute_but_preserve_u1() -> None:
    payload = berger_u1_obstruction_payload()
    assert payload["commutator_D_at_two_stretches_norm"] > 1e-6
    assert payload["commutator_D_with_shape_derivative_norm"] > 1e-6
    assert payload["commutator_D_with_fiber_U1_norm"] < 1e-12
    assert payload["commutator_derivative_with_fiber_U1_norm"] < 1e-12
    assert payload["unrestricted_three_channel_wake_generated"] is False


def test_fiber_u1_commutes_for_multiple_blocks_and_stretches() -> None:
    for n in range(1, 6):
        generator = fiber_u1_generator(n)
        for stretch in (0.8, 1.0, 1.4, 3.2):
            block = berger_dirac_block(n, 1.0, stretch)
            assert np.linalg.norm(block @ generator - generator @ block) < 1e-11


def test_spectral_projector_detects_critical_kernel() -> None:
    block = berger_dirac_block(1, 1.0, 4.0)
    projector, kernel = spectral_nonzero_projector(block)
    assert kernel == 1
    residuals = projector_residuals(projector)
    assert max(residuals.values()) < 1e-12


def test_regular_cap_profiles_with_same_boundary_data_have_different_dtn() -> None:
    payload = cap_nonuniqueness_payload()
    assert payload["same_boundary_potential_value"] is True
    assert payload["same_regular_center_condition"] is True
    assert payload["different_dtn_map"] is True
    assert payload["dtn_difference"] > 0.0


def test_cap_first_variation_identity() -> None:
    parameters = CapParameters(steps=8192)
    payload = cap_nonuniqueness_payload(parameters)
    assert payload["analytic_first_variation"] == pytest.approx(cap_first_variation(parameters))
    assert payload["first_variation_residual"] < 2e-8


def test_low_spectrum_is_deterministic_and_gapped_at_frozen_stretch() -> None:
    rows = low_berger_spectrum(BergerParameters(n_max=6))
    assert len(rows) == 7
    assert all(row["hermitian_residual"] < 1e-12 for row in rows)
    assert min(row["smallest_absolute_eigenvalue"] for row in rows) > 0.5


def test_partial_projector_is_explicitly_not_full_projector() -> None:
    payload = partial_projector_payload()
    assert payload["spinor_projector_computable"] is True
    assert payload["physical_full_projector_valid"] is False
    assert payload["max_projector_residual"] < 1e-11


def test_operator_payload_round_residual_is_small() -> None:
    payload = exact_berger_operator_payload(BergerParameters(n_max=8))
    assert payload["round_block_max_residual"] < 1e-11
    assert payload["physical_background_claimed"] is False


def test_parameter_validation_fail_closed() -> None:
    with pytest.raises(ValueError):
        validate_berger(BergerParameters(radius=0.0))
    with pytest.raises(ValueError):
        validate_berger(BergerParameters(stretch=-1.0))
    with pytest.raises(ValueError):
        validate_cap(CapParameters(kappa=0.0))
    with pytest.raises(ValueError):
        validate_cap(CapParameters(steps=4))


def test_physical_readiness_remains_false() -> None:
    payload = physical_readiness_payload()
    assert payload["mathematical_operator_advance_valid"] is True
    assert payload["physical_operator_bundle_valid"] is False
    assert payload["checks"]["exact_homogeneous_Dirac_blocks"] is True
    assert payload["checks"]["action_stationary_child_cap_background"] is False
    assert payload["physical_prediction_emitted"] is False


def test_completion_gate_remains_open() -> None:
    gate = completion_gate_payload()
    assert gate["full_BHSM_complete"] is False
    assert gate["mark_III"] == "NOT_REACHED"
    assert gate["usb_touched"] is False
    assert gate["exact_next_object"] == EXACT_NEXT_OBJECT


def test_artifact_materialization_is_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    paths_first = materialize(first)
    paths_second = materialize(second)
    assert len(paths_first) == len(paths_second) == len(artifact_payloads()) == 7
    for a, b in zip(paths_first, paths_second):
        assert a.name == b.name
        assert a.read_bytes() == b.read_bytes()
        json.loads(a.read_text(encoding="utf-8"))
