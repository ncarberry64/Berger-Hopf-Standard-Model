from __future__ import annotations

import pytest

from bhsm.interface.envelopment.support_action_v10_4 import (
    ACTION_VERDICT,
    canonical_depth,
    support_action_payload,
)


def test_two_healthy_kinetic_families_prove_canonical_nonuniqueness():
    constant = canonical_depth(0.5, family="constant_kinetic")
    logarithmic = canonical_depth(0.5, family="logarithmic_kinetic")
    assert constant == pytest.approx(0.5)
    assert logarithmic == pytest.approx(0.6931471805599453)
    assert constant != logarithmic
    with pytest.raises(ValueError):
        canonical_depth(0.5, family="unknown")


def test_support_action_is_audited_without_adopting_functions():
    payload = support_action_payload()
    assert payload["validation_passed"] is True
    assert payload["selected_Z_upsilon"] is None
    assert payload["selected_U_upsilon"] is None
    assert payload["action_owned_q_D"] is None
    assert payload["verdict"] == ACTION_VERDICT
    assert len(payload["coupling_ledger"]) == 4
