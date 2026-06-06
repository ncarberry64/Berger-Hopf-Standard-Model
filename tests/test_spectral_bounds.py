import numpy as np

from claims import ClaimStatus, build_claims_ledger
from ht_operator import alpha_scaled_a, default_level2_config
from positivity import complement_projector, psd_barrier_from_q
from spectral_bounds import (
    basis_convergence_scan,
    complement_gap_bound,
    gershgorin_lower_bound,
    heat_lift_lower_bound,
    minmax_bound,
    mu_h_target,
    psd_profile_bound,
    required_dirac_lower_bound,
    spectral_bound_report,
    weyl_lower_bound,
)
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL_2,
    DiracOperatorConfig,
    build_dirac_basis,
    build_level2_dirac_matrix,
    zero_mode_subspace,
)


def test_mu_h_target_and_heat_lift_bound_match_supplied_target():
    d_lower = 1.0

    assert mu_h_target() == MU_H
    assert heat_lift_lower_bound(d_lower, natural_lambda2(), MU_H) < MU_H + d_lower


def test_required_dirac_bound_uses_natural_cutoff_without_tuning():
    required = required_dirac_lower_bound(natural_lambda2(), MU_H)
    report = spectral_bound_report()

    assert report["lambda2"] == natural_lambda2()
    assert required == report["required_dirac_lower_bound"]
    assert required > 0


def test_lower_bound_estimates_do_not_exceed_exact_finite_gap():
    report = spectral_bound_report()
    exact_d = report["exact_finite_basis_complement_eigenvalue"]
    exact_ht = report["exact_finite_basis_ht_gap"]

    for value in report["raw_dirac_lower_estimates"].values():
        assert value <= exact_d + 1e-9
    for bound in report["bounds"]:
        assert bound.lower_bound <= exact_ht + 1e-9
        assert bound.assumptions
        assert bound.limitations


def test_minmax_and_gershgorin_bounds_are_conservative_on_level2_matrix():
    config = default_level2_config()
    basis = build_dirac_basis(config.k_max, sectors=config.sectors)
    zero_modes = zero_mode_subspace(basis, index_count=3)
    projector = complement_projector(zero_modes)
    matrix = build_level2_dirac_matrix(config)
    dirac_squared = matrix.T @ matrix

    minmax = minmax_bound(dirac_squared, projector)
    restricted = projector @ dirac_squared @ projector
    gersh = gershgorin_lower_bound(restricted[3:, 3:])

    assert gersh <= minmax + 1e-9
    assert minmax > 0


def test_psd_perturbations_cannot_lower_weyl_bound():
    base = 1.25
    profile_lower = 0.5

    assert weyl_lower_bound(base, profile_lower) >= base


def test_psd_profile_bound_is_nonnegative_on_complement():
    config = default_level2_config()
    basis = build_dirac_basis(config.k_max, sectors=config.sectors)
    zero_modes = zero_mode_subspace(basis, index_count=3)
    projector = complement_projector(zero_modes)
    profile = psd_barrier_from_q(np.eye(len(basis)))

    assert psd_profile_bound(profile, projector) >= 0


def test_negative_perturbation_lowers_bound_and_can_fail():
    baseline = complement_gap_bound(1.4630400252994733, natural_lambda2(), mu_h=MU_H)
    weakened = complement_gap_bound(
        1.4630400252994733,
        natural_lambda2(),
        v_min=-2.0,
        mu_h=MU_H,
    )

    assert weakened.lower_bound < baseline.lower_bound
    assert weakened.passes is False


def test_report_keeps_theorem_and_claim_status_conservative():
    report = spectral_bound_report()
    claim = next(claim for claim in build_claims_ledger() if claim.id == "ht_proxy_spectral_gap")

    assert report["theorem_complete"] is False
    assert claim.status in (ClaimStatus.PROXY_AUDIT, ClaimStatus.OPEN)
    assert claim.status != ClaimStatus.VERIFIED_TEST


def test_basis_convergence_scan_zero_modes_stay_three_and_all_pass():
    rows = basis_convergence_scan(
        k_max_values=[4, 6, 8, 10, 12, 16],
        a_values=[0.573, 1.0, alpha_scaled_a()],
        config_factory=default_level2_config,
        lambda2=natural_lambda2(),
    )

    assert len(rows) == 18
    assert all(row["zero_mode_count"] == 3 for row in rows)
    assert all(row["passes"] is True for row in rows)
    assert all(row["theorem_complete"] is False for row in rows)


def test_basis_convergence_scan_reports_worst_margin():
    rows = basis_convergence_scan([4, 6], [1.0], default_level2_config, natural_lambda2())

    assert all("worst_margin" in row for row in rows)
    assert all(row["worst_margin"] == min(row["direct_margin"], row["gershgorin_margin"], row["minmax_margin"]) for row in rows)


def test_basis_size_increases_with_kmax_for_each_anisotropy():
    rows = basis_convergence_scan([4, 6, 8], [0.573, 1.0], default_level2_config, natural_lambda2())

    for a in {row["a"] for row in rows}:
        subset = [row for row in rows if row["a"] == a]
        sizes = [row["basis_size"] for row in sorted(subset, key=lambda row: row["k_max"])]
        assert sizes == sorted(sizes)
        assert len(set(sizes)) == len(sizes)


def test_basis_convergence_notes_are_explicit_for_every_row():
    rows = basis_convergence_scan([4, 6, 8], [1.0], default_level2_config, natural_lambda2())

    assert all(row["monotonicity_notes"] for row in rows)
    assert rows[0]["monotonicity_notes"] == "baseline basis for this anisotropy"


def test_nonmonotonic_decrease_is_reported_when_present():
    def factory(k_max: int, a: float) -> DiracOperatorConfig:
        base = default_level2_config(k_max=k_max, a=a)
        boundary = dict(base.boundary_params)
        boundary["complement_floor"] = 1.1 if k_max == 4 else 1.3
        return DiracOperatorConfig(
            a=base.a,
            k_max=base.k_max,
            sectors=base.sectors,
            twist_params=base.twist_params,
            boundary_params=boundary,
            include_chirality=base.include_chirality,
            operator_level=DIRAC_PROXY_LEVEL_2,
        )

    rows = basis_convergence_scan([4, 6], [1.0], factory, natural_lambda2())

    assert "nonmonotonic decrease" in rows[1]["monotonicity_notes"]


def test_basis_convergence_claim_status_remains_proxy_audit():
    claim = next(claim for claim in build_claims_ledger() if claim.id == "ht_proxy_spectral_gap")

    assert claim.status == ClaimStatus.PROXY_AUDIT
