import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import weak_double_projection_zvirt_bridge as bridge  # noqa: E402


AUDIT_JSON = ROOT / "data" / "bhsm_weak_double_projection_zvirt_bridge.json"
CLOSURE_MAP = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
DOC = ROOT / "docs" / "bhsm_weak_double_projection_zvirt_bridge.md"
STATUS_DOC = ROOT / "docs" / "current_bhsm_status.md"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_weak_doublet_dimension_is_two():
    assert [door.name for door in bridge.weak_doublet_space()] == [
        "door_upper",
        "door_lower",
    ]
    assert bridge.weak_doublet_dimension() == 2


def test_up_weak_projector_rank_is_one():
    assert bridge.up_weak_projector_matrix() == ((1, 0), (0, 0))
    assert bridge.up_weak_projector_rank() == 1


def test_weak_double_projection_factor_is_one_half():
    assert bridge.weak_double_projection_factor() == Fraction(1, 2)


def test_actual_middle_up_dressing_path_uses_weak_double_projection():
    payload = bridge.actual_middle_up_rule_payload()
    assert payload["sector"] == "up_quarks"
    assert payload["generation"] == "middle"
    assert payload["mode"] == (6, 0)
    assert payload["q"] == 6
    assert payload["j"] == 0
    assert payload["omega_u"] == 6
    assert payload["source"] == "WEAK_DOUBLE_PROJECTION"
    assert payload["factor"] == Fraction(1, 2)
    assert bridge.actual_source_path_is_linked()


def test_statuses_upgrade_only_when_source_path_is_linked():
    linked = bridge.z_virt_statuses(linked=True)
    assert linked["Z_virt_u2_applicability"] == "DERIVED_CONDITIONAL"
    assert linked["Z_virt_u2_dimension_ratio"] == "DERIVED_CONDITIONAL"
    assert linked["legacy_Z_virt_u2_numerical_candidate"] == (
        "SUPERSEDED_BY_WEAK_DOUBLE_PROJECTION_BRIDGE"
    )

    unlinked = bridge.z_virt_statuses(linked=False)
    assert unlinked["Z_virt_u2_applicability"] == "OPEN_LOCALIZABLE"
    assert unlinked["Z_virt_u2_dimension_ratio"] == "STRONG_DERIVATION_CANDIDATE"
    assert unlinked["legacy_Z_virt_u2_numerical_candidate"] == "LOCALIZED_NOT_DERIVED"


def test_bridge_json_and_closure_map_statuses():
    audit = load_json(AUDIT_JSON)
    closure = load_json(CLOSURE_MAP)
    assert audit["public_status"] == bridge.PUBLIC_STATUS
    assert audit["weak_dimension"] == 2
    assert audit["projector_rank"] == 1
    assert audit["WEAK_DOUBLE_PROJECTION"] == "1/2"
    assert audit["actual_source_uses_weak_double_projection"] is True
    assert audit["Z_virt_u2_applicability"] == "DERIVED_CONDITIONAL"
    assert audit["Z_virt_u2_dimension_ratio"] == "DERIVED_CONDITIONAL"
    assert audit["legacy_Z_virt_u2_numerical_candidate"] == (
        "SUPERSEDED_BY_WEAK_DOUBLE_PROJECTION_BRIDGE"
    )

    assert closure["Z_virt_u2_applicability"]["status"] == "DERIVED_CONDITIONAL"
    assert closure["Z_virt_u2_dimension_ratio"]["status"] == "DERIVED_CONDITIONAL"
    assert closure["WEAK_DOUBLE_PROJECTION"]["status"] == "DERIVED_CONDITIONAL"
    assert closure["legacy_Z_virt_u2_numerical_candidate"]["status"] == (
        "SUPERSEDED_BY_WEAK_DOUBLE_PROJECTION_BRIDGE"
    )


def test_no_observed_data_is_used_by_bridge_source():
    source = (ROOT / "src" / "weak_double_projection_zvirt_bridge.py").read_text(
        encoding="utf-8"
    )
    forbidden_imports = (
        "mass_scheme",
        "prediction_ledger",
        "residual_audit",
        "ckm",
        "pmns",
        "neutrino",
        "quark_running",
    )
    for name in forbidden_imports:
        assert f"import {name}" not in source
        assert f"from {name}" not in source

    audit = load_json(AUDIT_JSON)
    assert audit["uses_observed_data"] is False
    for item in ("charm/top ratio", "up/top ratio", "CKM values", "PMNS values", "measured alpha"):
        assert item in audit["forbidden_inputs"]


def test_docs_preserve_public_status_and_no_prediction_change():
    combined = DOC.read_text(encoding="utf-8") + "\n" + STATUS_DOC.read_text(encoding="utf-8")
    assert bridge.PUBLIC_STATUS in combined
    assert "Z_virt_u2_applicability: DERIVED_CONDITIONAL" in combined
    assert "full virtual loop/threshold source remains open" in combined
    assert "not change frozen predictions" in combined
    forbidden = (
        "BHSM is proven",
        "BHSM is complete",
        "empirically validated",
        "numerically closed",
        "observed ratios justify",
    )
    for phrase in forbidden:
        assert phrase not in combined


def test_frozen_prediction_files_remain_unchanged_by_bridge():
    assert FROZEN_MD.exists()
    assert FROZEN_JSON.exists()
    report = bridge.build_bridge()
    assert report.frozen_predictions_changed is False
    assert report.official_predictions_changed is False
