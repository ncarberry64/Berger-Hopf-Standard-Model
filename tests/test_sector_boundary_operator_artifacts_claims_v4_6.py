import json
from pathlib import Path

from bhsm.interface.sector_boundary_operator import INVALIDATIONS, OPEN_GATES

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    "bhsm_sector_boundary_operator_v4_6.md",
    "bhsm_whitened_gauge_action_v4_6.md",
    "bhsm_boundary_operator_gauge_domain_v4_6.md",
    "bhsm_operator_lower_order_terms_v4_6.md",
    "bhsm_v4_6_status_and_open_gates.md",
)


def test_v4_6_artifacts_parse_and_preserve_prediction_guards():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*v4_6*.json"))
    selected = [path for path in paths if any(token in path.name for token in ("sector_boundary_operator", "whitened_gauge_action", "boundary_operator_principal_symbol", "frame_normalized_principal_residue", "gauge_fixed_domain_gate", "lower_order_operator_terms_gate", "v4_6_open_gates"))]
    assert len(selected) == 7
    for path in selected:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert set(OPEN_GATES).issubset(payload["open_gates"])


def test_docs_include_doctrine_domain_gate_lower_terms_and_no_go_notes():
    text = "\n".join((ROOT / "docs" / name).read_text(encoding="utf-8") for name in DOCS)
    assert "active adjoint-valued boundary one-form fluctuations" in text
    assert "B_i=L_i(ρ)^{1/2}A_i" in text
    assert "τ_frame=1/3" in text
    assert "OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN" in text
    assert "OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS" in text
    for invalidation in INVALIDATIONS:
        assert invalidation in text


def test_public_claims_reject_every_downstream_overclaim():
    new_docs_text = "\n".join((ROOT / "docs" / name).read_text(encoding="utf-8") for name in DOCS)
    public_status_text = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("CLAIMS.md", "STATUS.md"))
    forbidden = (
        "gauge couplings are fully derived",
        "g2_BH is action-derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "full BHSM is complete",
        "w=(1,2,7) are gauge-boson counts",
    )
    assert not any(phrase in new_docs_text for phrase in forbidden)
    assert "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION" in public_status_text
    assert "CKM_EXPONENT_NOT_DERIVED" in public_status_text
    assert "FULL_BHSM_NOT_COMPLETE" in public_status_text
