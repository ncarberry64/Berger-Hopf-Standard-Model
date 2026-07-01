from bhsm.interface.ckm_bounded_interface_normalization import audit_projector_domain_codomain


def test_projector_domain_codomain_stays_open_with_all_alternatives():
    payload = audit_projector_domain_codomain()
    assert payload["selection_status"] == "OPEN_MISSING_PROJECTOR_DOMAIN_CODOMAIN_SELECTION"
    assert payload["selected_space"] is None
    assert payload["selected_dimension"] is None
    dimensions = {row["space"]: row["dimension"] for row in payload["candidate_spaces"]}
    assert dimensions["Hom(V_u,V_d)"] == 8
    assert dimensions["Hom(V_u,V_d) direct_sum Hom(V_d,V_u)"] == 16
    assert dimensions["End(V_d)"] == 16
    assert dimensions["End(V_l) direct_sum End(V_u) direct_sum End(V_d)"] == 21
    assert dimensions["End(V_ch)"] == 49
