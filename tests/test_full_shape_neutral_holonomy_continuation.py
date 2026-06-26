import sys
from fractions import Fraction
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import boundary_relative_holonomy_cp as cp
import charged_effective_bridge_balance as balance
import charged_shape_freeze as shape
import ckm_structural_source as ckm
import neutral_bridge_pmns_source as neutral_bridge
import neutral_minimal_hessian as neutral_hessian


FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_charged_bridge_balance_rho3_gbridge_and_asymmetry_vector():
    assert balance.g_bridge() == Fraction(16, 189)
    assert balance.g_bridge_factorization() == Fraction(16, 189)
    records = {record.sector: record for record in balance.bridge_balance_records()}
    assert records["lepton"].tangent_norm_sq == 7
    assert records["up"].tangent_norm_sq == 7
    assert records["down"].tangent_norm_sq == 19
    assert records["lepton"].beta_f == Fraction(16, 1323)
    assert records["lepton"].kappa_f == Fraction(16, 1323)
    assert records["up"].beta_f == Fraction(32, 1323)
    assert records["up"].kappa_f == Fraction(16, 1323)
    assert records["down"].beta_f == Fraction(64, 1323)
    assert records["down"].kappa_f == Fraction(16, 3591)
    assert tuple(records[s].beta_over_kappa for s in ("lepton", "up", "down")) == (
        Fraction(1),
        Fraction(2),
        Fraction(76, 7),
    )
    assert records["up"].threshold_projection == Fraction(1, 2)
    assert records["up"].effective_balance == 1


def test_charged_shape_freeze_candidate_residual_and_symbolic_proximity():
    assert abs(shape.shape_ratio("lepton") - 2.7691182004266452) < 1e-10
    assert abs(shape.shape_ratio("up") - 1.7320903371870042) < 1e-10
    assert abs(shape.shape_ratio("down") - 1.0370279264765931) < 1e-10
    assert abs(shape.tri_sector_residual()) < 1e-6
    deltas = shape.symbolic_shape_deltas()
    assert abs(deltas["up"]) < 1e-4
    assert abs(deltas["down"]) < 1e-3
    assert abs(deltas["lepton"]) < 1e-3
    assert shape.STATUS_TABLE["charged_full_numerical_closure"] == "OPEN"


def test_neutral_minimal_hessian_candidate_diagnostics():
    diag = neutral_hessian.diagnostic()
    assert diag.matrix == ((1, 1), (1, 2))
    assert diag.determinant == 1
    assert diag.positive_definite is True
    assert diag.cost_3_0 == 9
    assert diag.cost_1_1 == 5
    assert diag.tangent == (-2, 1)
    assert diag.tangent_norm == 2
    assert diag.status == "STRONGLY_SUPPORTED_CANDIDATE_BY_MINIMAL_UNIMODULAR_MIXING"


def test_neutral_bridge_pmns_structural_seeds_are_candidate_only():
    diag = neutral_bridge.diagnostic()
    assert diag.eta_nu == Fraction(1, 3)
    assert diag.g_nu == Fraction(1, 3)
    assert diag.beta_nu == Fraction(1, 3)
    assert diag.kappa_nu == Fraction(1, 6)
    assert diag.K_nu == (
        (Fraction(0), Fraction(1, 3), Fraction(0)),
        (Fraction(1, 3), Fraction(3), Fraction(1, 6)),
        (Fraction(0), Fraction(1, 6), Fraction(5, 3)),
    )
    assert diag.excitation_inversion is True
    assert diag.theta_01 == Fraction(1, 9)
    assert diag.theta_12 == Fraction(1, 8)
    assert diag.theta_02 == Fraction(1, 90)
    assert diag.theta_l_01 == Fraction(4, 585)
    assert diag.theta_l_12 == Fraction(4, 1035)
    assert neutral_bridge.STATUS_TABLE["PMNS_numerical_closure"] == "OPEN"


def test_ckm_structural_source_down_near_degeneracy_vs_up_gap():
    diag = ckm.diagnostic()
    assert diag.down_N_d1 == 27
    assert diag.down_N_d2 == 28
    assert diag.down_cost_difference == 1
    assert diag.down_rule_A_diagonal_gap == Fraction(68, 147)
    assert diag.up_N_u1 == 36
    assert diag.up_N_u2 == 67
    assert diag.up_lambda_u1_without_ln2 == Fraction(456, 49)
    assert diag.up_lambda_u2 == Fraction(2546, 147)
    assert diag.up_threshold_gap_label == "1178/147 - ln2"
    assert diag.theta_12_d == Fraction(28, 2907)
    assert ckm.theta_12_u_numeric() > 0
    assert ckm.STATUS_TABLE["CKM_numerical_closure"] == "OPEN"


def test_boundary_relative_holonomy_phase_invariance_and_nontrivial_relative_phase():
    real = cp.real_tridiagonal(0.0, 3.0, 5.0, 1.0 / 3.0, 1.0 / 6.0)
    complex_matrix = cp.complex_tridiagonal(
        0.0, 3.0, 5.0, 1.0 / 3.0, 1.0 / 6.0, np.pi / 3, np.pi / 6
    )
    assert np.allclose(np.linalg.eigvalsh(real), np.linalg.eigvalsh(complex_matrix))
    assert cp.single_sector_eigenvalues_preserved()
    assert abs(cp.relative_holonomy(0.0, 0.0, np.pi / 3, 0.0) - np.pi / 3) < 1e-12
    assert cp.diagnostic().nontrivial is True
    assert cp.STATUS_TABLE["CKM_CP_closure"] == "OPEN"
    assert cp.STATUS_TABLE["PMNS_CP_closure"] == "OPEN"


def test_reports_preserve_guardrails_and_candidate_statuses():
    reports = (
        balance.report_as_dict(),
        shape.report_as_dict(),
        neutral_hessian.report_as_dict(),
        neutral_bridge.report_as_dict(),
        ckm.report_as_dict(),
        cp.report_as_dict(),
    )
    for report in reports:
        assert report["public_status"] == balance.PUBLIC_STATUS
        assert report["frozen_predictions_changed"] is False
        assert report["official_predictions_changed"] is False
        assert "OPEN" in str(report["statuses"])
    assert shape.report_as_dict()["statuses"]["charged_full_numerical_closure"] == "OPEN"


def test_no_empirical_input_fixture_introduced():
    combined = "\n".join(
        Path(module.__file__).read_text(encoding="utf-8")
        for module in (balance, shape, neutral_hessian, neutral_bridge, ckm, cp)
    )
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "observed_mass",
        "CKM data",
        "PMNS data",
        "neutrino data",
        "empirical target",
    )
    for item in blocked:
        assert item not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
