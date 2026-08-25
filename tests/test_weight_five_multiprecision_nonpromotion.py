from scripts.audit_n12_weight_five_multiprecision_nonpromotion import (
    build_payload,
)


def test_multiprecision_nonpromotion_payload():
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["multiprecision_bordered_solve"] == "DERIVED"
    assert payload["claim_boundary"]["weight_five_coefficient"] == "OPEN_NOT_PROMOTED"
    assert payload["tail_diagnostics"]["tight_coefficient_enclosure_certified"] is False
    assert payload["adjudication"]["full_remainder_outcome_promoted"] is False
