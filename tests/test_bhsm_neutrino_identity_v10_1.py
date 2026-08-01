from bhsm.interface.envelopment import neutrino_identity as neutrino


def test_neutrino_doctrine_does_not_create_a_static_rest_output():
    row = neutrino.neutrino_doctrine_gate()
    assert row["author_status"] == "AUTHOR_ONTOLOGY"
    assert row["physical_equivalence_status"] == "OPEN_PHYSICAL_EQUIVALENCE"
    assert row["exists_only_when_observed"] is False
    assert row["stationary_rest_branch_assigned"] is False
    assert row["primitive_static_mass_assigned"] is False


def test_dirac_majorana_and_propagation_observables_remain_open():
    payload = neutrino.neutrino_payload()
    observables = payload["observables"]
    assert payload["validation_passed"] is True
    assert observables["propagating_orbit"] is None
    assert observables["vertex_phase_map"] is None
    assert observables["neutrinoless_double_beta_decay"] is None
    assert observables["PMNS"] is None
    assert observables["Delta_m2"] is None
    assert observables["measured_oscillation_inputs_used"] is False
    assert payload["verdict"] == "BHSM_NEUTRINO_DIRAC_MAJORANA_OBSERVABLE_DISTINCTION_REMAINS_OPEN"
