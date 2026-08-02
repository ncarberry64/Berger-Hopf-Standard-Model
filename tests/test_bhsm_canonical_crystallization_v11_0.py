from bhsm.interface.envelopment.canonical_crystallization_v11_0 import (
    buoyancy_payload,
    charge_payload,
    core_transfer_payload,
    dependency_payload,
    falsification_payload,
    higgs_payload,
    ontology_payload,
    quantum_measurement_payload,
)


def test_canonical_ontology_is_typed_without_promoting_hypotheses():
    payload = ontology_payload()
    assert payload["validation_passed"] is True
    assert payload["physical_completion_claimed"] is False
    rows = {row["key"]: row for row in payload["entries"]}
    assert rows["logarithmic_depth"]["physical_theorem"] is True
    assert rows["haar_metric"]["physical_theorem"] is True
    assert rows["topological_buoyancy"]["physical_theorem"] is False
    assert rows["higgs"]["physical_theorem"] is False
    assert rows["quantum"]["physical_theorem"] is False
    assert rows["three_modes"]["statement"] != rows["generations"]["statement"]


def test_dependency_graph_has_one_open_upstream_object_and_no_false_closure():
    payload = dependency_payload()
    assert payload["validation_passed"] is True
    assert payload["acyclic_by_declared_order"] is True
    open_rows = [row for row in payload["nodes"] if row["status"] == "OPEN_HIGHEST_UPSTREAM"]
    assert len(open_rows) == 1
    assert open_rows[0]["object"] == payload["highest_upstream_open_object"]
    assert all(row["status"] != "CLOSED" for row in payload["nodes"][2:])


def test_canonical_physical_hypotheses_remain_fail_closed():
    assert core_transfer_payload()["transfer_operator"] is None
    assert buoyancy_payload()["displaced_energy_functional"] is None
    assert higgs_payload()["normalized_scalar_mode"] is None
    assert charge_payload()["geometric_assignments"] is None
    assert quantum_measurement_payload()["measurement_channel"] is None
    falsification = falsification_payload()
    assert falsification["physical_rejection_tests_run"] is False
    assert all(row["evaluated"] is False for row in falsification["rows"])
