from __future__ import annotations

from bhsm.interface.ae4_current_c2_physical_enclosure_state_integration import (
    claim_boundary,
    hindsight_supersession_contract,
    reconciled_identification_rows,
    transport_composition_contract,
)
from scripts.materialize_ae4_current_c2_physical_enclosure_state_integration import (
    build_payload,
)


def test_hindsight_supersedes_only_the_unchanged_ae2_no_carrier_result() -> None:
    result = hindsight_supersession_contract()
    assert result["old_kernel_A_no_carrier_is_current"] is False
    assert result["current_kernel_A_localization_carrier_closed"] is True
    assert result["canonical_stop_relabelled_as_spacetime_edge"] is False
    assert result["canonical_stop_used_as_localization_surface"] is False


def test_transport_reuses_particle_identity_without_rebuild() -> None:
    result = transport_composition_contract()
    assert "Pi_(r,n)" in result["intertwining_identity"]
    assert result["particle_spectrum_rebuilt"] is False
    assert result["new_particle_label_introduced"] is False


def test_reconciliation_reduces_the_open_rows_to_interacting_values() -> None:
    rows = reconciled_identification_rows()
    assert rows["PEI_03"]["status"] == "CLOSED"
    assert rows["PEI_04"]["status"] == "CLOSED"
    assert rows["PEI_11"]["status"] == "CLOSED_WITHOUT_SPECTRUM_REBUILD"
    assert "VALUES_OPEN" in rows["PEI_06"]["status"]
    assert "OPEN" in rows["PEI_07"]["status"]
    assert "OPEN" in rows["PEI_09"]["status"]


def test_claim_boundary_promotes_local_bridge_not_full_ae4_completion() -> None:
    result = claim_boundary()
    assert result["BHSM_NATIVE_PARTICLE_STATE_TO_LOCAL_ENCLOSURE_BRIDGE_DERIVED"]
    assert result[
        "PHYSICAL_ENCAPSULATION_IDENTIFIED_AT_LOCAL_CARRIER_AND_STATE_TRANSPORT_LEVEL"
    ]
    assert not result[
        "PHYSICAL_ENCAPSULATION_IDENTIFIED_AT_COMPLETE_AE4_INTERACTING_LEVEL"
    ]
    assert not result["PARTICLE_SPECTRUM_REBUILT"]
    assert not result["FULL_BHSM_COMPLETE"]


def test_materialized_integration_validates_all_nine_state_fibers() -> None:
    payload = build_payload()
    assert payload["validation_passed"]
    assert len(payload["scientific_result"]["nine_state_fibers"]) == 9
    assert payload["museum_export"]["local_enclosure_state_transport"] == "BHSM_DERIVED"
    assert payload["museum_export"]["complete_interacting_AE4_encapsulation"] == (
        "NOT_YET_DERIVED"
    )
