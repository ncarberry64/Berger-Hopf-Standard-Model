from bhsm.interface.aether_persistent_nonequilibrium_child_v17_87 import (
    completion_payload,
    persistence_and_decay_contract,
    stability_reclassification_ledger,
)


def test_particle_is_persistent_nonequilibrium_child_not_fixed_point():
    contract = persistence_and_decay_contract()
    assert "PERSISTENT_NONEQUILIBRIUM_CHILD" in contract["particle_definition"]
    assert "B_child" in contract["persistence"]
    assert contract["decay"]["definition"].startswith("tau_decay=inf")


def test_stability_results_are_reclassified_not_deleted():
    classes = {row["classification"] for row in stability_reclassification_ledger()}
    assert "KEEP_AS_LOCAL_MATHEMATICAL_CONDITION" in classes
    assert "REINTERPRET_AS_PERSISTENCE_CONDITION" in classes
    assert "INVALIDATE_AS_FINAL_PARTICLE_REQUIREMENT" in classes


def test_action_owned_imbalance_contract_validates():
    payload = completion_payload()
    assert payload["validation_passed"] is True
    diagnostics = payload["whole_child_imbalance"]["action_derived_diagnostics"]
    assert diagnostics["nonzero_nonequilibrium_momentum"] is True
