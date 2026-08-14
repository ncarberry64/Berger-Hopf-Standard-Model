import math

from bhsm.interface.aether_n3_terminal_child_boundary_map_v17_85 import (
    completion_payload,
    event_child_datum_ownership_ledger,
)


def test_terminal_event_supplies_typed_child_boundary_input():
    payload = completion_payload()
    assert payload["validation_passed"] is True
    boundary = payload["terminal_event_boundary_data"]
    assert math.isclose(
        boundary["spatial_trace_Gamma0"]["f"], math.pi / 4.0,
        abs_tol=1.0e-15,
    )
    assert boundary["material_response"]["eta_Legendre"] > 0.0
    assert len(boundary["mode_state"]["terminal_q"]) == 10


def test_missing_data_are_owned_not_turned_into_variables():
    ledger = event_child_datum_ownership_ledger()
    scale = next(row for row in ledger if row["datum"] == "local_reconstruction_scale")
    imbalance = next(row for row in ledger if row["datum"] == "persistent_child_imbalance")
    assert scale["class"] == "MISSING"
    assert "BVP" in scale["owner"]
    assert imbalance["class"] == "POST-EVENT DYNAMIC"
