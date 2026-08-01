from bhsm.interface.envelopment import geometry_reconciliation as geometry


def test_domain_dimensions_and_ownership_are_consistent():
    payload = geometry.geometry_payload()
    assert payload["validation_passed"] is True
    rows = {row["object"]: row for row in payload["domains"]}
    assert rows["M8"]["dimension"] == 8
    assert rows["Hopf S3"]["dimension"] == 3
    assert rows["M5"]["dimension"] == 5
    assert rows["M4=B1"]["dimension"] == 4
    assert "global parent" in rows["M8"]["role"]
    assert "observable" in rows["M4=B1"]["role"]


def test_s3_times_m4_is_not_silently_identified_with_m8():
    row = geometry.s3_m4_identification()
    assert row["dimension"] == 7
    assert row["not_equal_to_M8_by_dimension"] is True
    assert row["global_product_claim"] is False
    assert "pi2(Sp(1))=0" in row["restriction_triviality_proof"]
    assert "I_rho" in row["eight_dimensional_completion"]
    assert geometry.GEOMETRY_VERDICT == "BHSM_S3_M4_IS_A_LOCAL_OR_REDUCED_DESCRIPTION_NOT_THE_FULL_PARENT"


def test_rho_radion_and_proxy_radius_remain_distinct():
    row = geometry.radial_ownership()
    assert row["rho"]["action_owned"] is True
    assert row["a_F"]["identified_with_sigma"] is False
    assert row["R"]["classification"] == "PROXY_ONLY"
    assert row["selected_buoyancy_coordinate"] is None
