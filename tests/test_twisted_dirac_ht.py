import numpy as np
import pytest

from ht_operator import (
    alpha_scaled_a,
    build_ht_spectrum,
    default_twist_parameter_grid,
    first_complement_gap,
    gap_report,
    passes_no_extra_light_gap,
    scan_twisted_dirac_robustness,
)
from positivity import psd_barrier_from_q
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL,
    build_dirac_basis,
    complement_spectrum,
    dirac_squared_spectrum,
    hopf_charge,
    twist_shift,
    zero_mode_subspace,
)


def _default_dirac_case(k_max=3):
    basis = build_dirac_basis(k_max=k_max)
    spectrum = dirac_squared_spectrum(
        basis,
        a=1.0,
        twist_params={"dirac_scale": 2.0, "boundary_strength": 0.05, "chirality_shift": 0.01},
    )
    zero_modes = zero_mode_subspace(basis, index_count=3)
    return basis, spectrum, zero_modes


def test_dirac_basis_includes_chirality_labels():
    basis = build_dirac_basis(k_max=2, sectors=["lepton"], include_chirality=True)

    assert {mode.chirality for mode in basis} == {-1, 1}
    assert all(mode.sector == "lepton" for mode in basis)
    assert all(mode.q == hopf_charge(mode.k, mode.j) for mode in basis)


def test_hopf_charges_are_correct():
    assert hopf_charge(5, 2) == 1
    assert hopf_charge(10, 1) == 8
    assert hopf_charge(6, 3) == 0


def test_twist_shift_uses_sector_chirality_hopf_and_boundary_data():
    basis = build_dirac_basis(k_max=1, sectors=["lepton"])
    mode = next(item for item in basis if item.k == 1 and item.j == 0 and item.chirality == 1)
    shift = twist_shift(
        mode,
        {
            "sector_shifts": {"lepton": 0.2},
            "chirality_shift": 0.1,
            "hopf_shift": 0.05,
            "boundary_strength": 0.01,
        },
    )

    assert shift != 0.0


def test_zero_mode_subspace_inserts_exactly_three_modes():
    basis = build_dirac_basis(k_max=2)
    zero_modes = zero_mode_subspace(basis, index_count=3)

    assert zero_modes.shape == (len(basis), 3)
    assert np.allclose(zero_modes[:3, :], np.eye(3))


def test_complement_spectrum_excludes_protected_zero_modes():
    basis, spectrum, zero_modes = _default_dirac_case()
    complement = complement_spectrum(spectrum, zero_modes)
    protected = {0, 1, 2}

    assert len(complement) == len(basis) - 3
    assert all(int(row["index"]) not in protected for row in complement)
    assert all(row["model_level"] == DIRAC_PROXY_LEVEL for row in complement)


def test_ht_heat_lift_preserves_zero_modes_when_dirac_squared_is_zero():
    dirac_spectrum = np.array(
        [
            {"index": 0, "mode": None, "dirac_eigenvalue": 0.0, "eigenvalue": 0.0},
            {"index": 1, "mode": None, "dirac_eigenvalue": 1.0, "eigenvalue": 1.0},
        ],
        dtype=object,
    )
    ht = build_ht_spectrum(dirac_spectrum, lambda2=natural_lambda2(), mu_h=MU_H)

    assert ht[0]["ht_eigenvalue"] == 0.0


def test_psd_profile_terms_do_not_reduce_complement_gap():
    _, spectrum, zero_modes = _default_dirac_case()
    base_report = gap_report(spectrum, zero_modes)
    profile = psd_barrier_from_q(np.eye(len(spectrum)))
    psd_report = gap_report(spectrum, zero_modes, profile_term=profile)

    assert psd_report["first_ht_complement_gap"] >= base_report["first_ht_complement_gap"]
    assert psd_report["passes_mu_h"] is True


def test_negative_profile_terms_require_explicit_failure_flag_and_can_break_gap():
    _, spectrum, zero_modes = _default_dirac_case()
    negative = np.full(len(spectrum), -0.01 * MU_H)

    with pytest.raises(ValueError):
        build_ht_spectrum(spectrum, lambda2=natural_lambda2(), mu_h=MU_H, profile_term=negative)

    report = gap_report(
        spectrum,
        zero_modes,
        profile_term=negative,
        allow_negative_profile=True,
    )
    assert report["passes_mu_h"] is False


def test_gap_report_does_not_claim_theorem_completion():
    _, spectrum, zero_modes = _default_dirac_case()
    ht = build_ht_spectrum(spectrum, lambda2=None, mu_h=MU_H)
    report = gap_report(spectrum, zero_modes)

    assert all(row["theorem_complete"] is False for row in ht)
    assert report["theorem_complete"] is False
    assert report["model_level"] == DIRAC_PROXY_LEVEL


def test_first_complement_gap_and_pass_flag_are_explicit():
    _, spectrum, zero_modes = _default_dirac_case()
    ht = build_ht_spectrum(spectrum, lambda2=natural_lambda2(), mu_h=MU_H)
    first = first_complement_gap(ht, zero_modes)

    assert isinstance(passes_no_extra_light_gap(ht, zero_modes, MU_H), bool)
    assert first["ht_eigenvalue"] >= MU_H


def test_robustness_scan_results_are_explicit_and_theorem_open():
    rows = scan_twisted_dirac_robustness(
        k_max_values=[4],
        a_values=[1.0],
        twist_param_grid=default_twist_parameter_grid()[:1],
    )

    assert len(rows) == 1
    assert type(rows[0]["passes"]) is bool
    assert rows[0]["theorem_complete"] is False
    assert rows[0]["model_level"] == DIRAC_PROXY_LEVEL


def test_robustness_baseline_passes_and_zero_count_is_three():
    rows = scan_twisted_dirac_robustness(
        k_max_values=[4],
        a_values=[1.0],
        twist_param_grid=default_twist_parameter_grid()[:1],
        sectors=[("lepton", "up", "down")],
    )

    assert rows[0]["passes"] is True
    assert rows[0]["zero_mode_count"] == 3


def test_robustness_failures_are_reported_not_hidden():
    rows = scan_twisted_dirac_robustness(
        k_max_values=[4],
        a_values=[0.573],
        twist_param_grid=[{"dirac_scale": 1.0, "boundary_strength": 0.0, "chirality_shift": 0.0}],
        profile_model="negative_failure",
    )

    assert len(rows) == 1
    assert rows[0]["passes"] is False
    assert rows[0]["margin"] < 0.0


def test_negative_profile_terms_remain_forbidden_by_default():
    _, spectrum, _ = _default_dirac_case()
    negative = np.full(len(spectrum), -0.01 * MU_H)

    with pytest.raises(ValueError):
        build_ht_spectrum(spectrum, lambda2=None, mu_h=MU_H, profile_term=negative)


def test_scan_negative_profile_failure_is_explicitly_labeled():
    rows = scan_twisted_dirac_robustness(
        k_max_values=[4],
        a_values=[1.0],
        twist_param_grid=default_twist_parameter_grid()[:1],
        profile_model="negative_failure",
    )

    assert rows[0]["profile_model"] == "negative_failure"
    assert rows[0]["passes"] is False


def test_scan_psd_profile_does_not_reduce_gap():
    base = scan_twisted_dirac_robustness(
        k_max_values=[4],
        a_values=[1.0],
        twist_param_grid=default_twist_parameter_grid()[:1],
        profile_model="zero",
    )[0]
    psd = scan_twisted_dirac_robustness(
        k_max_values=[4],
        a_values=[1.0],
        twist_param_grid=default_twist_parameter_grid()[:1],
        profile_model="psd_identity",
    )[0]

    assert psd["first_ht_gap"] >= base["first_ht_gap"]
    assert psd["margin"] >= base["margin"]


def test_scan_supports_sector_cases_and_alpha_scaled_a():
    rows = scan_twisted_dirac_robustness(
        k_max_values=[4],
        a_values=[0.573, 1.0, alpha_scaled_a()],
        twist_param_grid=default_twist_parameter_grid()[:1],
        sectors=[("lepton", "up", "down"), ("lepton",), ("up",), ("down",)],
    )

    assert len(rows) == 12
    assert {row["sectors"] for row in rows} == {
        ("lepton", "up", "down"),
        ("lepton",),
        ("up",),
        ("down",),
    }
