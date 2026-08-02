from __future__ import annotations

from bhsm.interface.envelopment.support_weight_derivation_v11_0 import (
    NEXT_EXACT_OBJECT,
    PRIMARY_VERDICT,
    supported_action_payload,
)


def test_composition_fixes_character_form_but_not_weights_or_haar_scale():
    payload = supported_action_payload()
    assert payload["validation_passed"] is True
    assert payload["lambda_D_fixed"] is False
    assert payload["support_weights_fixed"] is False
    assert payload["complete_supported_parent_action"] is None
    assert payload["status"] == PRIMARY_VERDICT
    assert payload["next_exact_object"] == NEXT_EXACT_OBJECT


def test_two_integer_weight_assignments_prove_remaining_nonuniqueness():
    rows = supported_action_payload()["admissible_counterexamples"]
    assert [(row["w_C"], row["w_W"]) for row in rows] == [(1, 1), (1, 2)]
    assert all(row["F_C_at_one"] == row["F_W_at_one"] == 1.0 for row in rows)
    assert rows[0]["canonical_slopes_at_lambda_one"] != rows[1]["canonical_slopes_at_lambda_one"]
    assert all(row["adopted"] is False for row in rows)
