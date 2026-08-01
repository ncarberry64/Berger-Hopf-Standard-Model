from __future__ import annotations

from bhsm.interface.envelopment.core_stratum_matching_v10_4 import core_matching_payload


def test_core_matching_separates_terminal_and_flux_ensembles():
    payload = core_matching_payload()
    assert payload["validation_passed"] is True
    assert payload["complete_junction_law"] is False
    assert payload["internal_core_action"] is None
    assert payload["variational_ensembles"]["dirichlet_terminal"]["transfer_claim_allowed"] is False
    assert payload["variational_ensembles"]["flux_matching"]["extra_scalar_boundary_action"] == "OPEN"
    assert payload["absorption_or_emission"] is None
    assert payload["fundamental_dissipation"] is False
