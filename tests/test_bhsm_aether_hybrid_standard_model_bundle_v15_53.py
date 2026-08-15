from bhsm.interface import aether_hybrid_standard_model_bundle_v15_53 as sm


def test_rank16_three_family_chiral_bundle_and_faithful_quotient():
    bundle = sm.chiral_bundle_contract()
    assert bundle["one_family_complex_dimension"] == 16
    assert bundle["families"] == 3
    assert bundle["faithful_gauge_group"].endswith("/Z6")
    assert max(sm.z6_kernel_residuals().values()) < 1e-13


def test_geometric_hypercharge_yukawa_and_anomalies_close():
    selection = sm.hypercharge_selection()
    assert selection["selected_quark_doublet_charge"] == "1/6"
    assert selection["selected_lepton_doublet_charge"] == "-1/2"
    ledger = sm.yukawa_and_anomaly_ledger()
    assert ledger["all_Yukawa_vertices_gauge_invariant"]
    assert ledger["all_local_anomalies_zero"]
    assert ledger["global_Sp1_Witten_anomaly_absent"]


def test_hybrid_event_returns_bundle_isomorphism_class_without_connections():
    gluing = sm.hybrid_bundle_gluing()
    assert gluing["connection_one_forms_transported_as_pregeometric_primitives"] is False
    assert gluing["hybrid_bundle_returns_to_same_isomorphism_class"]
    payload = sm.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["mass_eigenvalues_and_mixing_derived"] is False


def test_payload_json_is_deterministic():
    payload = sm.completion_payload()
    assert sm.deterministic_json(payload) == sm.deterministic_json(
        sm.completion_payload()
    )
