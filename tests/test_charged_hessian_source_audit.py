import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import charged_hessian_source_audit as audit  # noqa: E402


AUDIT_JSON = ROOT / "data" / "bhsm_charged_hessian_source_audit.json"
CLOSURE_MAP = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
SOURCE_DOC = ROOT / "docs" / "bhsm_charged_hessian_source_audit.md"
STATUS_DOC = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_rho_1_produces_old_costs_conditionally():
    assert audit.old_costs_are_conditional_on_rho_1()
    assert audit.charged_metric_costs(1) == {
        "lepton": [0, 5, 18],
        "up": [0, 36, 65],
        "down": [0, 9, 20],
    }
    assert audit.audit_statuses()["rho_ch_1_minimal_closure"] == (
        "MINIMAL_ACTION_CLOSURE_CANDIDATE"
    )


def test_rho_3_produces_cyclic_costs_conditionally():
    assert audit.cyclic_costs_are_conditional_on_rho_3()
    assert audit.charged_metric_costs(3) == {
        "lepton": [0, 13, 36],
        "up": [0, 36, 67],
        "down": [0, 27, 28],
    }
    assert audit.audit_statuses()["rho_ch_3_cyclic_weight"] == (
        "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    )
    assert audit.no_action_source_decides_rho()


def test_down_membership_and_ordering_constraints():
    assert audit.down_membership_constraint(Fraction(1, 10))
    assert audit.down_membership_constraint(Fraction(79, 10))
    assert not audit.down_membership_constraint(0)
    assert not audit.down_membership_constraint(8)

    assert audit.down_ordering_constraint(Fraction(31, 10))
    assert not audit.down_ordering_constraint(Fraction(16, 5))
    assert not audit.down_ordering_constraint(4)


def test_eta_l_exact_value_remains_open_when_rho_ch_open():
    status = audit.eta_l_status("OPEN_LOCALIZABLE")
    assert status["eta_l_exact_value"] == "OPEN"
    assert status["eta_l_depends_on_rho_ch"] is True
    assert status["eta_l_can_be_derived"] is False
    assert status["eta_l_fit"] == "FORBIDDEN_AS_DERIVATION"
    assert audit.audit_statuses()["eta_l_depends_on_rho_ch"] == "TRUE"


def test_charged_cross_term_forbidden_and_neutral_mixing_separated():
    assert audit.cross_term_status(False) == "FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED"
    rows = {row.object: row for row in audit.source_audit_rows()}
    neutral = rows["neutral/topographic Berger anisotropy"]
    charged_cross = rows["charged qj cross-term"]
    assert neutral.neutral_topographic_only is True
    assert neutral.charged_sector_applicable is False
    assert neutral.status == "OPEN_ALLOWED_NEUTRAL_ONLY"
    assert charged_cross.status == "FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED"


def test_machine_readable_source_audit_and_closure_map_statuses():
    source = load_json(AUDIT_JSON)
    closure = load_json(CLOSURE_MAP)
    required = {
        "charged_Hessian_source_audit": "COMPLETED",
        "rho_ch_1_minimal_closure": "MINIMAL_ACTION_CLOSURE_CANDIDATE",
        "rho_ch_3_cyclic_weight": "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        "rho_ch_action_value": "OPEN_LOCALIZABLE",
        "charged_Hessian_anisotropy_rho_ch": "OPEN_LOCALIZABLE",
        "charged_qj_cross_term": "FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED",
        "neutral_qj_mixing": "OPEN_ALLOWED",
        "topographic_Berger_anisotropy_to_charged_sector": (
            "FORBIDDEN_UNLESS_EXPLICIT_COUPLING_DERIVED"
        ),
        "eta_l_projection_structure": "VALIDATED_CANDIDATE",
        "eta_l_exact_value": "OPEN",
        "eta_l_fit": "FORBIDDEN_AS_DERIVATION",
        "eta_l_8_over_9_trace_route": "DOWNGRADED_NUMERICAL_COINCIDENCE",
        "alpha_geom_internal_derivation": "OPEN_LOCALIZABLE",
        "Pi_l_value": "OPEN_LOCALIZABLE",
        "self_screening_factor_1_minus_alpha_geom": "STRUCTURALLY_SUPPORTED_CANDIDATE",
    }
    for key, expected in required.items():
        assert source[key] == expected
        assert closure[key]["status"] == expected

    assert source["eta_l_depends_on_rho_ch"] is True
    assert closure["eta_l_depends_on_rho_ch"]["status"] == "TRUE"
    assert source["source_audit_result"] == "NO_ACTION_SOURCE_DECIDES_RHO_CH"
    assert source["frozen_predictions_changed"] is False
    assert source["official_predictions_changed"] is False


def test_no_empirical_or_prediction_modules_choose_rho_ch():
    source = (ROOT / "src" / "charged_hessian_source_audit.py").read_text(encoding="utf-8")
    forbidden_imports = (
        "mass_scheme",
        "prediction_ledger",
        "residual_audit",
        "ckm",
        "pmns",
        "neutrino",
    )
    for name in forbidden_imports:
        assert f"import {name}" not in source
        assert f"from {name}" not in source

    audit_json = load_json(AUDIT_JSON)
    assert "measured alpha" in audit_json["forbidden_inputs"]
    assert "empirical target values" in audit_json["forbidden_inputs"]


def test_docs_preserve_public_status_and_guardrails():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (SOURCE_DOC, STATUS_DOC, CLAIM_TABLE, BACKLOG)
    )
    assert audit.PUBLIC_STATUS in combined
    assert "rho_ch_action_value: OPEN_LOCALIZABLE" in combined
    assert "charged_qj_cross_term: FORBIDDEN_CONDITIONAL_UNLESS_ACTION_DERIVED" in combined
    assert "neutral_qj_mixing: OPEN_ALLOWED" in combined
    assert "eta_l_depends_on_rho_ch: TRUE" in combined
    assert "No numerical closure" in combined

    forbidden = (
        "BHSM is proven",
        "BHSM is complete",
        "empirically validated",
        "numerically closed",
        "BHSM replaces the Standard Model",
        "Standard Model is fully derived",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_are_not_part_of_source_audit():
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
    assert audit.rho_candidates_preserve_ledgers()
