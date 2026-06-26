import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_kf_bridge_coupling_kernel as bridge
import charged_kf_generator as kf


DATA = ROOT / "data" / "charged_kf_bridge_coupling_kernel_v1.json"
DOC = ROOT / "docs" / "charged_kf_bridge_coupling_kernel_v1.md"
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


def test_topology_is_tridiagonal_by_default():
    edges = bridge.enabled_topology_edges()
    assert edges == ((0, 1), (1, 2))
    assert (0, 2) not in edges
    rows = {row.edge: row for row in bridge.bridge_topology()}
    assert rows[(0, 1)].status == "DERIVED_CONDITIONAL_ON_RANK_THREE_CLOSURE_LADDER"
    assert rows[(1, 2)].status == "DERIVED_CONDITIONAL_ON_ZERO_DEFECT_TANGENT_ADJACENCY"
    assert rows[(0, 2)].enabled is False
    assert rows[(0, 2)].status == "NOT_ASSUMED_REQUIRES_CYCLIC_E3_ACTION_SOURCE"


def test_cyclic_edge_requires_explicit_source():
    assert (0, 2) not in bridge.enabled_topology_edges(cyclic_source_present=False)
    assert (0, 2) in bridge.enabled_topology_edges(cyclic_source_present=True)


def test_beta_minimal_ansatz_values_and_open_magnitude_status():
    rows = {row.sector: row for row in bridge.reference_bridge_candidates()}
    assert rows["lepton"].beta_f == Fraction(1, 147)
    assert rows["up"].beta_f == Fraction(2, 147)
    assert rows["down"].beta_f == Fraction(4, 147)
    for row in rows.values():
        assert row.topology_status == "DERIVED_CONDITIONAL_ON_E3_LADDER"
        assert row.magnitude_status == "OPEN_LOCALIZABLE"
        assert row.ansatz_status == "STRONGLY_SUPPORTED_CANDIDATE"
        assert row.magnitude_status != "DERIVED_CONDITIONAL"


def test_kappa_minimal_ansatz_values_and_open_magnitude_status():
    for rho in kf.RHO_CH_BRANCHES:
        rows = {row.sector: row for row in bridge.tangent_bridge_candidates(rho)}
        assert rows["lepton"].kappa_f == Fraction(1, 21 * (4 + rho))
        assert rows["up"].kappa_f == Fraction(1, 21 * (4 + rho))
        assert rows["down"].kappa_f == Fraction(1, 21 * (16 + rho))
        assert rows["lepton"].tangent_norm_sq == 4 + rho
        assert rows["up"].tangent_norm_sq == 4 + rho
        assert rows["down"].tangent_norm_sq == 16 + rho
        for row in rows.values():
            assert row.topology_status == "DERIVED_CONDITIONAL_ON_ZERO_DEFECT_TANGENT_ADJACENCY"
            assert row.inverse_stiffness_status == "STRONGLY_SUPPORTED_CANDIDATE"
            assert row.magnitude_status == "OPEN_LOCALIZABLE"
            assert row.magnitude_status != "DERIVED_CONDITIONAL"


def test_named_bridge_rules_in_generator():
    assert kf.bridge_rule_status(kf.BRIDGE_RULE_DIAGONAL_ONLY) == "BASELINE_DIAGNOSTIC"
    assert kf.bridge_rule_status(kf.BRIDGE_RULE_MINIMAL_ANSATZ) == "STRONGLY_SUPPORTED_CANDIDATE"
    assert kf.bridge_rule_status(kf.BRIDGE_RULE_SYMBOLIC_OPEN) == (
        "TOPOLOGY_PRESENT_MAGNITUDES_OPEN"
    )

    diagonal = kf.minimal_K_f_for_rule(
        "up",
        1,
        kf.RULE_A_SINGLE_OPERATOR_TRACE,
        kf.BRIDGE_RULE_DIAGONAL_ONLY,
    )
    assert diagonal[0][1] == diagonal[1][0] == 0
    assert diagonal[1][2] == diagonal[2][1] == 0

    minimal = kf.minimal_K_f_for_rule(
        "up",
        1,
        kf.RULE_A_SINGLE_OPERATOR_TRACE,
        kf.BRIDGE_RULE_MINIMAL_ANSATZ,
    )
    assert minimal[0][1] == minimal[1][0] == Fraction(2, 147)
    assert minimal[1][2] == minimal[2][1] == Fraction(1, 105)
    assert minimal == kf.minimal_K_f_for_rule("up", 1, kf.RULE_A_SINGLE_OPERATOR_TRACE)


def test_symbolic_open_bridge_rule_refuses_numeric_matrix():
    try:
        kf.minimal_K_f_for_rule(
            "up",
            1,
            kf.RULE_A_SINGLE_OPERATOR_TRACE,
            kf.BRIDGE_RULE_SYMBOLIC_OPEN,
        )
    except ValueError as exc:
        assert "topology but no numeric beta/kappa" in str(exc)
    else:
        raise AssertionError("symbolic-open bridge rule should not emit numeric beta/kappa")


def test_rule_a_suppression_does_not_derive_bridge_magnitudes():
    separation = bridge.suppression_bridge_separation()
    assert separation["status"] == "OPEN_LOCALIZABLE"
    assert separation["does_suppression_kernel_derive_beta0"] is False
    assert separation["does_suppression_kernel_derive_kappa0"] is False
    report = bridge.report_as_dict()
    assert report["statuses"]["beta_f_reference_bridge_magnitude"] == "OPEN_LOCALIZABLE"
    assert report["statuses"]["kappa_f_magnitude"] == "OPEN_LOCALIZABLE"
    assert report["verdict"]["bridge_magnitude_verdict"] == "BRIDGE_MAGNITUDES_OPEN_LOCALIZABLE"


def test_json_artifact_records_kernel_claim_boundary():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == bridge.PUBLIC_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["enabled_topology_edges"] == [[0, 1], [1, 2]]
    assert data["cyclic_0_2_enabled_by_default"] is False
    assert data["verdict"]["theorem_complete"] is False
    assert data["verdict"]["beta_f_open_localizable"] is True
    assert data["verdict"]["kappa_f_open_localizable"] is True
    assert data["minimal_ansatz_bridge_values_by_rho"]["1"]["lepton"]["beta_f"] == "1/147"
    assert data["minimal_ansatz_bridge_values_by_rho"]["1"]["up"]["kappa_f"] == "1/105"


def test_docs_status_backlog_preserve_public_status_and_open_closure():
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (DOC, CLAIMS, BACKLOG)
    )
    required = (
        bridge.PUBLIC_STATUS,
        "charged_Kf_bridge_coupling_kernel_v1",
        "charged_Kf_tridiagonal_bridge_topology",
        "E3_reference_ladder_bridge",
        "zero_defect_tangent_bridge",
        "beta_f_reference_bridge_magnitude=OPEN_LOCALIZABLE",
        "kappa_f_magnitude=OPEN_LOCALIZABLE",
        "suppression_bridge_coupling_identification=OPEN_LOCALIZABLE",
        "cyclic_0_2_bridge=NOT_ASSUMED_REQUIRES_CYCLIC_E3_ACTION_SOURCE",
        "numerical_closure=OPEN",
    )
    for phrase in required:
        assert phrase in combined

    forbidden = (
        "bridge magnitude derived",
        "beta_0 derived",
        "kappa_0 derived",
        "numerical closure achieved",
        "official predictions updated",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_no_empirical_imports_in_bridge_modules():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (Path(bridge.__file__), Path(kf.__file__))
    )
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "gauge_couplings",
        "reference_common_scale",
    )
    for item in blocked:
        assert item not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
    data = bridge.report_as_dict()
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
