import json

from bhsm.interface.provenance import ProvenanceChain, ProvenanceRecord, ValueWithProvenance


def test_provenance_is_json_serializable_and_booleans_are_explicit():
    record = ProvenanceRecord("artifact.json", "example", "value", "DISCOVERED", True, False, False, False, True, "INTERNAL")
    value = ValueWithProvenance("example", 1.0, "dimensionless", "scalar", record, ProvenanceChain((record,)))
    payload = value.to_dict()
    json.dumps(payload)
    for key in ("loaded_at_runtime", "empirical_derivation_input", "calibration_input", "reference_comparison_input", "frozen_prediction"):
        assert isinstance(payload[key], bool)
