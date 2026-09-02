import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_ACCEPTED_REPLAY_ACTION_BLOCK_SCREEN.json"
)


def test_coarse_field_descriptor_block_route_is_rigorously_obstructed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    assert payload["status"] == (
        "SAME_CENTER_FIELD_DESCRIPTOR_BLOCK_RADII_ROUTE_OBSTRUCTED"
    )
    assert payload["outward_center_defect"]["field_Y_lower"] > 0.0
    assert payload["existing_curvature_witness"]["input_block"] == "FIELD"
    assert payload["necessary_field_block_test"]["discriminant_upper"] < 0.0
    assert payload["decision"][
        "coarse_73_plus_1_field_descriptor_block_route_obstructed"
    ]
    assert not payload["decision"][
        "componentwise_or_finer_action_owned_partition_obstructed"
    ]
    assert not payload["decision"]["root_nonexistence_claim"]
    assert not payload["decision"]["physical_spacetime_instability_claim"]


def test_persisted_field_split_recombines_to_total_center_defect():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    data = np.load(ROOT / payload["data"])
    total = data["total_Y_lower_by_node"]
    field = data["field_Y_lower_by_node"]
    descriptor = data["descriptor_Y_upper_by_node"]
    assert total.shape == field.shape == descriptor.shape == (371,)
    assert np.all(total + 1.0e-20 >= field)
    assert int(np.argmax(total)) == payload["outward_center_defect"][
        "total_Y_owner_node"
    ]
