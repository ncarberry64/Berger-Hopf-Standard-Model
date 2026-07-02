import json
from pathlib import Path

from bhsm.interface.cli import main
from bhsm.interface.neutrino_bedrock import load_neutrino_bedrock_status


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "neutrino_bedrock_dynamic_layer_v1.json"


def test_artifact_exists_parses_and_locks_doctrine():
    assert ARTIFACT.is_file()
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["artifact_id"] == "NEUTRINO_BEDROCK_DYNAMIC_LAYER_V1"
    assert payload["status"] == "STRUCTURAL_DOCTRINE_LOCKED"


def test_allowed_and_forbidden_claims_are_separated():
    payload = load_neutrino_bedrock_status()
    assert "dimensionless PMNS constraints" in payload["bedrock_layer_allows"]
    assert "BHSM derives physical neutrino masses in eV" in payload["forbidden_claims"]
    assert "BHSM emits dimensionful mass by default" in payload["forbidden_claims"]


def test_open_neutral_scale_blockers_remain_open():
    payload = load_neutrino_bedrock_status()
    blockers = set(payload["dynamic_layer_open_blockers"])
    assert {
        "OPEN_MISSING_NEUTRAL_SCALE",
        "OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
        "DIMENSIONFUL_MASS_NOT_AVAILABLE",
    } <= blockers


def test_claims_document_has_explicit_no_overclaim_language():
    claims = (ROOT / "CLAIMS.md").read_text(encoding="utf-8")
    assert "BHSM may constrain dimensionless PMNS geometry." in claims
    assert "BHSM does not emit physical eV/GeV neutrino masses by default." in claims
    assert "BHSM replaces QFT local dynamics" in claims


def test_status_distinguishes_bedrock_and_dynamic_layers():
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    assert "BEDROCK_LAYER_BHSM" in status
    assert "DYNAMIC_LAYER_QFT_SM" in status
    assert "## Bedrock Blockers" in status
    assert "## Dynamic-Layer Deferred Blockers" in status


def test_cli_emits_machine_readable_status(capsys):
    assert main(["neutrino-bedrock-status", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "STRUCTURAL_DOCTRINE_LOCKED"


def test_frozen_and_official_outputs_are_untouched():
    payload = load_neutrino_bedrock_status()
    assert payload["frozen_predictions_modified"] is False
    assert payload["official_prediction_logic_modified"] is False
