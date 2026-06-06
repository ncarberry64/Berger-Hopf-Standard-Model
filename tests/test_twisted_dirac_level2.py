import numpy as np
import pytest

from claims import build_claims_ledger
from ht_operator import (
    alpha_scaled_a,
    build_ht_from_level2_dirac,
    default_level2_config,
    default_level2_perturbations,
    level2_ht_gap_report,
    scan_level2_ht_robustness,
)
from positivity import psd_barrier_from_q
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL_2,
    build_dirac_basis,
    build_level2_dirac_matrix,
    level2_dirac_squared_spectrum,
    zero_mode_subspace,
)


def test_level2_matrix_is_symmetric():
    matrix = build_level2_dirac_matrix(default_level2_config())

    assert np.allclose(matrix, matrix.T)


def test_level2_spectrum_is_real():
    spectrum = level2_dirac_squared_spectrum(default_level2_config())

    assert all(isinstance(row["eigenvalue"], float) for row in spectrum)
    assert all(row["eigenvalue"] >= 0 for row in spectrum)


def test_level2_zero_mode_count_is_three_in_baseline():
    config = default_level2_config()
    basis = build_dirac_basis(config.k_max, sectors=config.sectors)
    zero_modes = zero_mode_subspace(basis, index_count=3)
    spectrum = level2_dirac_squared_spectrum(config)

    assert zero_modes.shape[1] == 3
    assert [row["eigenvalue"] for row in spectrum[:3]] == [0.0, 0.0, 0.0]


def test_level2_heat_term_preserves_protected_zero_modes():
    ht_spectrum, _ = build_ht_from_level2_dirac(default_level2_config(), natural_lambda2())

    assert [row["ht_eigenvalue"] for row in ht_spectrum[:3]] == [0.0, 0.0, 0.0]


def test_level2_complement_gap_passes_in_baseline():
    report = level2_ht_gap_report(default_level2_config(), natural_lambda2())

    assert report["passes"] is True
    assert report["first_ht_complement_gap"] >= MU_H
    assert report["model_level"] == DIRAC_PROXY_LEVEL_2


def test_level2_psd_profile_does_not_reduce_gap():
    config = default_level2_config()
    base = level2_ht_gap_report(config, natural_lambda2())
    size = base["basis_size"]
    profile = psd_barrier_from_q(np.eye(size))
    with_profile = level2_ht_gap_report(config, natural_lambda2(), profile_operator=profile)

    assert with_profile["first_ht_complement_gap"] >= base["first_ht_complement_gap"]


def test_level2_negative_profile_forbidden_by_default():
    config = default_level2_config()
    negative = np.full(len(build_dirac_basis(config.k_max, sectors=config.sectors)), -0.01 * MU_H)

    with pytest.raises(ValueError):
        build_ht_from_level2_dirac(config, natural_lambda2(), profile_operator=negative)


def test_level2_theorem_complete_remains_false_and_claim_not_upgraded():
    report = level2_ht_gap_report(default_level2_config(), natural_lambda2())
    claim = next(claim for claim in build_claims_ledger() if claim.id == "ht_proxy_spectral_gap")

    assert report["theorem_complete"] is False
    assert claim.status.value == "PROXY_AUDIT"
    assert "open" in " ".join(claim.limitations).lower()


def test_level2_robustness_scan_reports_required_fields():
    rows = scan_level2_ht_robustness(
        k_max_values=[4, 6, 8],
        a_values=[0.573, 1.0, alpha_scaled_a()],
        perturbations=default_level2_perturbations(),
        lambda2=natural_lambda2(),
    )

    assert len(rows) == 27
    assert all(row["zero_mode_count"] == 3 for row in rows)
    assert all(type(row["passes"]) is bool for row in rows)
    assert all(row["theorem_complete"] is False for row in rows)
    assert all(row["model_level"] == DIRAC_PROXY_LEVEL_2 for row in rows)
