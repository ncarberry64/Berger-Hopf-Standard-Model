from __future__ import annotations

from bhsm.interface.envelopment.core_stratum_action_v11_0 import (
    CORE_NEXT_OBJECT,
    CORE_VERDICT,
    core_action_payload,
)


def test_core_is_an_asymptotic_haar_endpoint_and_transfer_is_not_invented():
    payload = core_action_payload()
    assert payload["validation_passed"] is True
    assert "q_D=+infinity" in payload["core_boundary"]
    assert payload["complete_flux_relation"] is False
    assert payload["reversible_absorption_emission"] is False
    assert payload["minimal_core_action"] is None
    assert payload["status"] == CORE_VERDICT
    assert payload["next_exact_object"] == CORE_NEXT_OBJECT


def test_conservation_alone_does_not_select_a_core_transfer_law():
    rows = core_action_payload()["conservative_counterexamples"]
    assert len(rows) == 2
    assert all(row["regular_symplectic_flux"] == 0 for row in rows)
    assert all(row["transfer"] is False for row in rows)
