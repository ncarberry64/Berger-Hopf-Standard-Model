import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import charged_kf_generator as kf  # noqa: E402


DATA_JSON = ROOT / "data" / "bhsm_full_freeze_protocol_charged_kf_v1.json"
FREEZE_DOC = ROOT / "docs" / "bhsm_freeze_protocol.md"
TABLE_DOC = ROOT / "docs" / "charged_kf_candidate_tables.md"
CLAIM_STATUS = ROOT / "docs" / "claim_status_table.md"
CURRENT_STATUS = ROOT / "docs" / "current_bhsm_status.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sector_formula_values():
    rows = {row.sector: row for row in kf.sector_rows()}
    assert rows["neutrino"].omega_expression == "-q - 2j"
    assert rows["neutrino"].T == -3
    assert rows["lepton"].omega_expression == "-q + 2j"
    assert rows["lepton"].T == 3
    assert rows["up"].omega_expression == "q - 2j"
    assert rows["up"].T == 6
    assert rows["down"].omega_expression == "q + 4j"
    assert rows["down"].T == 12

    assert kf.omega(0, +1, 3, 0) == -3
    assert kf.omega(0, -1, 1, 2) == 3
    assert kf.omega(1, +1, 6, 0) == 6
    assert kf.omega(1, -1, 0, 3) == 12


def test_ledgers_have_reference_slot_and_nonzero_modes_satisfy_zero_defect():
    for sector, ledger in kf.LEDGERS.items():
        assert kf.is_reference_slot(ledger[0])
        for mode in ledger[1:]:
            assert kf.mode_satisfies_sector_equation(sector, mode)
            C, sigma = kf.SECTORS[sector]
            assert kf.delta_IT(C, sigma, *mode) == 0


def test_tangent_adjacencies_match_declared_sector_engine():
    assert kf.tangent_difference("neutrino") == (-2, 1)
    assert kf.tangent_difference("lepton") == (2, 1)
    assert kf.tangent_difference("up") == (2, 1)
    assert kf.tangent_difference("down") == (4, -1)


def test_charged_suppression_fractions_are_exact():
    assert kf.g_ch() == Fraction(1, 21)
    assert kf.projection_fraction("lepton") == Fraction(1, 7)
    assert kf.projection_fraction("up") == Fraction(2, 7)
    assert kf.projection_fraction("down") == Fraction(4, 7)
    assert kf.self_screening("lepton") == Fraction(20, 21)
    assert kf.self_screening("up") == Fraction(19, 21)
    assert kf.self_screening("down") == Fraction(17, 21)
    assert kf.eta("lepton") == Fraction(20, 3087)
    assert kf.eta("up") == Fraction(38, 3087)
    assert kf.eta("down") == Fraction(68, 3087)


def test_charged_costs_for_all_rho_branches():
    assert set(kf.RHO_CH_BRANCHES) == {1, 2, 3}
    assert kf.diagonal_costs("lepton", 1) == (0, 5, 18)
    assert kf.diagonal_costs("up", 1) == (0, 36, 65)
    assert kf.diagonal_costs("down", 1) == (0, 9, 20)
    assert kf.diagonal_costs("lepton", 3) == (0, 13, 36)
    assert kf.diagonal_costs("up", 3) == (0, 36, 67)
    assert kf.diagonal_costs("down", 3) == (0, 27, 28)


def test_minimal_Kf_template_is_real_symmetric_tridiagonal():
    for rho in kf.RHO_CH_BRANCHES:
        for sector in kf.CHARGED_SECTORS:
            matrix = kf.minimal_K_f(sector, rho)
            assert len(matrix) == 3
            assert all(len(row) == 3 for row in matrix)
            assert matrix[0][2] == 0
            assert matrix[2][0] == 0
            assert matrix[0][1] == matrix[1][0]
            assert matrix[1][2] == matrix[2][1]
            assert all(isinstance(value, Fraction) for row in matrix for value in row)


def test_beta_and_kappa_bridges_are_exact():
    for rho in kf.RHO_CH_BRANCHES:
        assert kf.beta("lepton") == Fraction(1, 147)
        assert kf.beta("up") == Fraction(2, 147)
        assert kf.beta("down") == Fraction(4, 147)
        assert kf.kappa("lepton", rho) == Fraction(1, 21 * (4 + rho))
        assert kf.kappa("up", rho) == Fraction(1, 21 * (4 + rho))
        assert kf.kappa("down", rho) == Fraction(1, 21 * (16 + rho))


def test_threshold_insertion_is_operator_level_and_only_middle_up():
    insertions = kf.threshold_insertions()
    assert insertions == [
        {
            "sector": "up",
            "slot": 1,
            "mode": [6, 0],
            "value": "ln 2",
            "source": "Z_virt^{u,2}=1/2 weak-double projection bridge",
            "operator_level": True,
        }
    ]
    for rho in kf.RHO_CH_BRANCHES:
        bare = kf.minimal_K_f("up", rho)
        dressed = kf.dressed_K_u(rho)
        assert dressed[1][1] > float(bare[1][1])
        assert dressed[0][0] == float(bare[0][0])
        assert dressed[2][2] == float(bare[2][2])
        assert dressed[0][1] == float(bare[0][1])
        assert dressed[1][2] == float(bare[1][2])


def test_eigenvalue_reports_are_deterministic_diagnostics():
    reports = kf.all_branch_reports()
    assert set(reports) == {1, 2, 3}
    for sector_reports in reports.values():
        assert set(sector_reports) == set(kf.CHARGED_SECTORS)
        for report in sector_reports.values():
            assert len(report.eigenvalues) == 3
            assert report.eigenvalues == tuple(sorted(report.eigenvalues))
            assert report.gaps_from_ground[0] == 0


def test_statuses_and_generated_data_preserve_claim_boundary():
    data = load_json(DATA_JSON)
    assert data["public_status"] == kf.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    for status_key, status in kf.STATUS_TABLE.items():
        assert data["statuses"][status_key] == status
    assert data["statuses"]["rho_ch_exact_value"] == "OPEN_LOCALIZABLE"
    assert data["statuses"]["numerical_closure"] == "OPEN"


def test_docs_preserve_public_status_and_no_overclaiming():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (FREEZE_DOC, TABLE_DOC, CLAIM_STATUS, CURRENT_STATUS)
    )
    assert kf.PUBLIC_STATUS in combined
    assert "minimal_charged_Kf_generator: STRONGLY_SUPPORTED_CANDIDATE" in combined
    assert "rho_ch_exact_value: OPEN_LOCALIZABLE" in combined
    assert "numerical_closure: OPEN" in combined
    forbidden = (
        "BHSM is proven",
        "numerically closed",
        "empirically validated",
        "observed masses derive",
        "CKM data derive",
        "PMNS data derive",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_generator_does_not_import_empirical_or_prediction_modules():
    source = (ROOT / "src" / "charged_kf_generator.py").read_text(encoding="utf-8")
    forbidden_imports = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "neutrino",
        "reference_common_scale",
    )
    for name in forbidden_imports:
        assert f"import {name}" not in source
        assert f"from {name}" not in source


def test_frozen_prediction_files_remain_unchanged_by_candidate_generator():
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
    report = kf.report_as_dict()
    assert report["frozen_predictions_changed"] is False
    assert report["official_predictions_changed"] is False
