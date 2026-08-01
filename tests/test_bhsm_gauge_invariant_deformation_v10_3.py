from bhsm.interface.envelopment import gauge_invariant_deformation_v10_3 as deformation


def test_normal_radion_combination_is_exactly_gauge_invariant():
    row = deformation.radial_gauge_invariant()
    assert row["residual"] == "0"
    assert row["invariant"] is True
    assert row["coefficient_inserted"] is False


def test_homogeneous_limit_leaves_radion_but_not_buoyancy_mode():
    payload = deformation.deformation_payload()
    assert payload["validation_passed"] is True
    assert payload["canonical_mode"]["physical_scalar_count_in_invariant_M8_sector"] == 1
    assert payload["canonical_mode"]["buoyancy_eligible_count"] == 0


def test_prior_fold_mode_is_not_rebranded_as_depth():
    row = deformation.fold_mode_firewall()
    assert row["conditional_kinetic_norm"] > 0
    assert row["same_as_beta"] is False
    assert row["same_as_psi"] is False
    assert row["physical_depth"] is False
