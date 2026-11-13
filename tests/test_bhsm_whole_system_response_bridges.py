"""The integration witness must reuse core data and retain physical gates."""

import json

import bhsm.interface.ae4_current_c2_factorized_hs_calderon as core
from scripts.materialize_bhsm_whole_system_response_bridges import build_payload


def test_saved_core_to_mixed_response_witness_reproduces_without_campaign(monkeypatch):
    def forbid_recompute(**kwargs):
        raise AssertionError("integration must reuse the saved fixed core")

    monkeypatch.setattr(core, "factorized_product_dirac_hs_weyl_jet", forbid_recompute)
    first = json.dumps(build_payload(), sort_keys=True, allow_nan=False)
    second = json.dumps(build_payload(), sort_keys=True, allow_nan=False)
    assert first == second
    result = json.loads(first)
    assert result["validation_passed"]
    assert len(result["finite_event_witness"]["jet_labels"]) == 4
    assert not result["physical_event_response_evaluated"]
    assert not result["scalar_HS_reference_to_physical_sector_projection_derived"]
    assert not result["FULL_BHSM_COMPLETE"]
    assert not result["Gate7_background_or_proof_contract_changed"]
    assert not result["pole_to_lepton_invariant_bridge"]["physical_family_poles_supplied"]
