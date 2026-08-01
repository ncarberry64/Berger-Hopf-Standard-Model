from bhsm.interface.envelopment import full_configuration_space_v10_3 as configuration


def test_prior_work_is_imported_without_conflating_distinct_modes():
    rows = configuration.prior_work_equivalence_ledger()
    assert len(rows) == 6
    fold = next(row for row in rows if "fold amplitude" in row["earlier_name"])
    assert fold["same_object"] is False
    radion = next(row for row in rows if row["v10_3_name"] == "localized Hopf radion")
    assert radion["same_object"] is True


def test_current_configuration_keeps_embedding_fixed_and_counts_gauge_modes_zero():
    payload = configuration.configuration_payload()
    assert payload["validation_passed"] is True
    assert "varied X:M4->M8" in payload["configuration_space"]["not_in_current_configuration_space"]
    rows = {row["candidate"]: row for row in payload["scalar_degree_ledger"]}
    assert rows["rho coordinate shift"]["physical_scalar_count"] == 0
    assert rows["B1 threading/endpoint trace"]["physical_scalar_count"] == 0
    assert payload["buoyancy_selected_physical_scalar_count"] == 0


def test_dirac_count_formula_fails_closed():
    assert configuration.physical_count(2, 1, 0) == 0
    assert configuration.physical_count(2, 0, 0) == 2
    try:
        configuration.physical_count(1, 1, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("negative physical phase-space count must fail")
