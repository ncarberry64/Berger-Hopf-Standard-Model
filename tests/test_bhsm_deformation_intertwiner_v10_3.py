from bhsm.interface.envelopment import deformation_intertwiner_v10_3 as intertwiner


def test_seam_fold_intertwiner_is_imported_not_rederived():
    payload = intertwiner.intertwiner_payload()
    row = payload["intertwiners"][0]
    assert row["operator"] == "U_zeta_to_psi"
    assert row["status"] == "DERIVED_CONDITIONAL"
    assert "tau*pi*chi_1/16" in row["map"]
    assert row["boundary_preservation"] is True
    assert row["source_preservation"] is True


def test_Hopf_intertwiners_and_equivalences_remain_unresolved():
    payload = intertwiner.intertwiner_payload()
    assert all(row["status"] == "UNDEFINED_CROSS_DOMAIN" for row in payload["intertwiners"][1:])
    assert payload["full_common_intertwiner"] is None
    assert payload["source_equivalence"] == "EQUIVALENCE_UNRESOLVED"
    assert payload["spectral_equivalence"] == "EQUIVALENCE_UNRESOLVED"
    assert payload["physically_inequivalent"] is False
