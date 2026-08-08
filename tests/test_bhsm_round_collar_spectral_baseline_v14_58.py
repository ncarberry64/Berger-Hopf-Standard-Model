from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.completion.round_collar_spectral_baseline_v14_58 import (
    EXACT_NEXT_OBJECT,
    RoundCollarParameters,
    artifact_payloads,
    child_finite_collar_dtn,
    completion_gate_payload,
    dirichlet_trace_certificate,
    dirichlet_trace_tail_upper_bound,
    dtn_contrast,
    dtn_contrast_matrix,
    materialize,
    mode_kappa,
    off_diagonal_norm,
    physical_readiness_payload,
    round_s3_dirac_laplace_mode,
    round_s3_scalar_laplace_mode,
    round_symmetry_obstruction_payload,
    scale_covariance_payload,
    stable_dirichlet_contrast,
    stable_neumann_contrast,
    validate_parameters,
    weighted_dirichlet_contrast_term,
)


def test_round_dirac_laplace_lowest_mode() -> None:
    mode = round_s3_dirac_laplace_mode(0, radius=2.0, mass=0.0)
    assert mode["dirac_eigenvalues"] == pytest.approx([-0.75, 0.75])
    assert mode["dirac_laplace_eigenvalue"] == pytest.approx(0.5625)
    assert mode["multiplicity"] == 4


def test_round_spinor_baseline_has_no_zero_mode() -> None:
    for n in range(20):
        assert round_s3_dirac_laplace_mode(n, 1.0, 0.0)["dirac_laplace_eigenvalue"] > 0.0


def test_scalar_baseline_exposes_massless_constant_zero_mode() -> None:
    mode = round_s3_scalar_laplace_mode(0, 1.0, 0.0)
    assert mode["eigenvalue"] == 0.0
    assert mode["multiplicity"] == 1


def test_dirichlet_and_neumann_dtn_bracket_parent() -> None:
    kappa = 1.7
    length = 0.9
    parent = kappa
    assert child_finite_collar_dtn(kappa, length, "dirichlet") > parent
    assert child_finite_collar_dtn(kappa, length, "neumann") < parent


def test_stable_contrast_formulas_match_direct_formulas() -> None:
    kappa = 2.3
    length = 0.7
    assert stable_dirichlet_contrast(kappa, length) == pytest.approx(
        dtn_contrast(kappa, length, "dirichlet"), rel=1e-13
    )
    assert stable_neumann_contrast(kappa, length) == pytest.approx(
        dtn_contrast(kappa, length, "neumann"), rel=1e-13
    )


def test_domain_choice_flips_contrast_sign() -> None:
    kappa = 1.0
    length = 1.0
    assert stable_dirichlet_contrast(kappa, length) > 0.0
    assert stable_neumann_contrast(kappa, length) < 0.0


def test_dirichlet_contrast_decays_with_mode_number() -> None:
    parameters = RoundCollarParameters()
    values = [stable_dirichlet_contrast(mode_kappa(n, parameters.radius, parameters.mass), parameters.collar_length) for n in range(12)]
    assert all(a > b for a, b in zip(values, values[1:]))


def test_trace_tail_bound_contains_computed_far_tail() -> None:
    parameters = RoundCollarParameters(n_max=24)
    bound = dirichlet_trace_tail_upper_bound(25, parameters)
    computed_far_tail = sum(weighted_dirichlet_contrast_term(n, parameters) for n in range(25, 400))
    assert computed_far_tail <= bound
    assert bound > 0.0


def test_trace_certificate_is_finite_and_tight() -> None:
    certificate = dirichlet_trace_certificate(RoundCollarParameters(n_max=64))
    assert math.isfinite(certificate["partial_trace_through_n_max"])
    assert certificate["tail_upper_bound"] < 1e-30
    low, high = certificate["certified_interval"]
    assert high >= low > 0.0


def test_round_homogeneous_block_is_central() -> None:
    matrix = dtn_contrast_matrix(1.8, 0.7, "dirichlet", 3)
    assert off_diagonal_norm(matrix) == 0.0
    arbitrary = np.array([[0, 1j, 0.2], [-1j, 0, 0.4j], [0.2, -0.4j, 0]], dtype=complex)
    assert np.linalg.norm(matrix @ arbitrary - arbitrary @ matrix) < 1e-14


def test_round_symmetry_obstruction_is_exact() -> None:
    payload = round_symmetry_obstruction_payload()
    assert payload["commutator_with_fourier_basis_norm"] < 1e-14
    assert payload["commutator_with_oriented_shape_generator_norm"] < 1e-14
    assert payload["noncentral_wake_generated"] is False


def test_scale_covariance() -> None:
    payload = scale_covariance_payload(scale=4.0)
    assert payload["absolute_residual"] < 1e-14
    assert payload["absolute_scale_selected"] is False


def test_parameter_validation_is_fail_closed() -> None:
    with pytest.raises(ValueError):
        validate_parameters(RoundCollarParameters(radius=0.0))
    with pytest.raises(ValueError):
        validate_parameters(RoundCollarParameters(collar_length=-1.0))
    with pytest.raises(ValueError):
        validate_parameters(RoundCollarParameters(mass=-0.1))


def test_physical_readiness_remains_false() -> None:
    payload = physical_readiness_payload()
    assert payload["reduced_analytic_baseline_valid"] is True
    assert payload["physical_operator_bundle_valid"] is False
    assert payload["checks"]["reduced_seam_dtn_difference_trace_class"] is True
    assert payload["checks"]["berger_anisotropic_dirac_spectrum"] is False
    assert payload["physical_prediction_emitted"] is False


def test_completion_gate_remains_open() -> None:
    gate = completion_gate_payload()
    assert gate["full_BHSM_complete"] is False
    assert gate["mark_III"] == "NOT_REACHED"
    assert gate["physical_neutrino_prediction_emitted"] is False
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
