import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import neutral_sector_operator_kernel as neutral


DATA = ROOT / "data" / "neutral_sector_operator_kernel_v1.json"
DOC = ROOT / "docs" / "neutral_sector_operator_kernel_v1.md"
CLAIMS = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def branch_by_id():
    return {branch.branch_id: branch for branch in neutral.neutral_hessian_branches()}


def test_neutrino_ledger_and_sector_equation():
    assert neutral.NEUTRINO_LEDGER == ((0, 0), (3, 0), (1, 1))
    assert neutral.NEUTRINO_SECTOR_EQUATION == "q + 2j = 3"
    for mode in neutral.nonzero_neutrino_modes():
        assert neutral.neutrino_sector_equation_value(*mode) == 3
    assert neutral.tangent_difference() == (-2, 1)
    assert neutral.NEUTRINO_TANGENT == (-2, 1)


def test_symbolic_hessian_form_and_psd_diagnostics():
    form = neutral.neutral_hessian_symbolic_form()
    assert form["matrix"] == "[[a,b],[b,c]]"
    assert form["cost"] == "N_nu(q,j)=a q^2 + 2b qj + c j^2"
    assert "ac-b^2>=0" in form["PSD_conditions"]

    branches = branch_by_id()
    n0 = neutral.positivity_diagnostic(branches["N0"])
    n2 = neutral.positivity_diagnostic(branches["N2"])
    assert n0.determinant == 1
    assert n0.positive_definite is True
    assert n2.determinant == 1
    assert n2.positive_definite is True


def test_neutral_branch_costs_are_exact_diagnostics():
    branches = branch_by_id()
    assert neutral.neutral_cost(3, 0, branches["N0"]) == 9
    assert neutral.neutral_cost(1, 1, branches["N0"]) == 2
    assert neutral.neutral_cost(3, 0, branches["N2"]) == 9
    assert neutral.neutral_cost(1, 1, branches["N2"]) == 5
    assert branches["N0"].status == "NEUTRAL_HESSIAN_BRANCH_CANDIDATE"
    assert branches["N2"].status == "STRUCTURALLY_MOTIVATED_CANDIDATE"
    assert branches["N1_rho_2"].status == "STRUCTURALLY_POSSIBLE_NOT_DERIVED"


def test_tangent_norm_diagnostics_exist_without_selecting_branch():
    rows = {row.branch_id: row for row in neutral.tangent_norm_diagnostics()}
    assert rows["N0"].tangent == (-2, 1)
    assert rows["N0"].norm_sq == 5
    assert rows["N2"].norm_sq == 2
    verdict = neutral.verdict()
    assert verdict.selected_hessian_branch is None
    assert verdict.neutral_numerical_closure == "OPEN"


def test_neutral_operator_templates_are_not_physical_predictions():
    symbolic = neutral.neutral_operator_template(neutral.NEUTRAL_OPERATOR_SYMBOLIC)
    assert symbolic.topology_edges == ((0, 1), (1, 2))
    assert symbolic.direct_0_2_bridge_enabled is False
    assert symbolic.eta_nu == "eta_nu_OPEN"
    assert symbolic.beta_nu == "beta_nu_OPEN"
    assert symbolic.kappa_nu == "kappa_nu_OPEN"
    assert symbolic.matrix_template[0][2] == "0"
    assert symbolic.physical_prediction is False

    unit = neutral.neutral_operator_template(neutral.NEUTRAL_OPERATOR_UNIT_DIAGNOSTIC)
    mixed = neutral.neutral_operator_template(
        neutral.NEUTRAL_OPERATOR_TOPOGRAPHIC_MIXED_DIAGNOSTIC
    )
    assert unit.physical_prediction is False
    assert mixed.matrix_template[1][1] == "N2(3,0)=9"
    assert mixed.matrix_template[2][2] == "N2(1,1)=5"
    assert mixed.physical_prediction is False


def test_neutral_thresholds_are_all_open_or_reference():
    rows = {row.mode: row for row in neutral.neutral_threshold_records()}
    assert rows[(0, 0)].is_reference_slot is True
    assert rows[(0, 0)].status == "REFERENCE_SLOT_NOT_THRESHOLD_TARGET"
    assert rows[(3, 0)].status == "NO_THRESHOLD_SOURCE_FOUND"
    assert rows[(1, 1)].status == "NO_THRESHOLD_SOURCE_FOUND"
    for row in rows.values():
        assert row.threshold_factor is None
        assert row.insertion is None


def test_pmns_placeholder_is_structural_only():
    placeholder = neutral.PMNS_placeholder()
    assert placeholder.formula == "U_PMNS = U_l^dagger U_nu"
    assert placeholder.structural_status == "STRUCTURALLY_MOTIVATED_CANDIDATE"
    assert placeholder.numerical_status == "OPEN"


def test_json_artifact_records_neutral_open_statuses():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == neutral.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["ledger"] == [[0, 0], [3, 0], [1, 1]]
    assert data["ledger_status"] == "DERIVED_CONDITIONAL_ON_SECTOR_ENGINE"
    assert data["statuses"]["neutral_sector_operator_kernel_v1"] == (
        "STRUCTURALLY_MOTIVATED_CANDIDATE"
    )
    assert data["statuses"]["neutral_numerical_closure"] == "OPEN"
    assert data["statuses"]["PMNS_numerical_closure"] == "OPEN"
    assert data["verdict"]["theorem_complete"] is False


def test_docs_status_backlog_preserve_neutral_boundaries():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, CLAIMS, BACKLOG)
    )
    required = (
        neutral.PUBLIC_STATUS,
        "neutral_sector_operator_kernel_v1",
        "neutrino_mode_ledger=DERIVED_CONDITIONAL_ON_SECTOR_ENGINE",
        "neutral_Hessian_symbolic_form=OPEN_LOCALIZABLE",
        "neutral_Hessian_branch_N0_isotropic",
        "neutral_Hessian_branch_N1_charged_like",
        "neutral_Hessian_branch_N2_topographic_mixed",
        "neutral_eta_source=OPEN_LOCALIZABLE",
        "neutral_threshold_operator=OPEN",
        "PMNS_structural_source=STRUCTURALLY_MOTIVATED_CANDIDATE",
        "PMNS_numerical_closure=OPEN",
        "neutral_numerical_closure=OPEN",
    )
    for phrase in required:
        assert phrase in combined

    forbidden = (
        "neutrino masses predicted",
        "PMNS closure achieved",
        "neutral numerical closure achieved",
        "official predictions updated",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_no_empirical_imports_in_neutral_module():
    source = Path(neutral.__file__).read_text(encoding="utf-8")
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "gauge_couplings",
        "reference_common_scale",
        "neutrino_mass",
    )
    for item in blocked:
        assert item not in source


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    data = neutral.report_as_dict()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
