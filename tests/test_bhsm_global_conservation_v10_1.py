from bhsm.interface.envelopment import global_conservation as conservation


def test_local_stress_identity_closes_on_shell_with_flux_qualification():
    row = conservation.local_noether_identity()
    assert row["on_shell_closed_value"] == 0
    assert row["on_shell_closed_conservation"] is True
    assert "boundary flux" in row["identity"]
    assert row["homogeneous_scalar_check"]["factorization_exact"] is True
    assert row["homogeneous_scalar_check"]["on_shell_value"] == 0


def test_parent_action_has_no_explicit_fundamental_dissipation():
    row = conservation.reversibility_audit()
    assert row["explicit_dissipative_terms"] == []
    assert row["nonlocal_memory_terms"] == []
    assert row["fundamental_time_arrow"] is False
    assert row["unitarity"].startswith("OPEN")


def test_topological_degree_is_scoped_and_total_cosmic_energy_fails_closed():
    topology = conservation.topology_conservation()
    energy = conservation.global_energy_audit()
    assert topology["charge"] == "N=deg(eta|Sigma7) in pi7(S7)=Z"
    assert "SMOOTH_FIXED_DOMAIN" in topology["verdict"]
    assert energy["ordinary_integral_T00_coordinate_independent"] is False
    assert energy["scalar_total_cosmic_energy"] is None
    assert conservation.CONSERVATION_VERDICT == "BHSM_SCALAR_TOTAL_COSMIC_ENERGY_NOT_COVARIANTLY_DEFINED"


def test_entropy_claim_requires_an_explicit_coarse_graining():
    row = conservation.entropy_gate()
    assert row["coarse_graining_map"] is None
    assert row["entropy_functional"] is None
    assert row["local_entropy_explained"] is False
    assert conservation.conservation_payload()["validation_passed"] is True
