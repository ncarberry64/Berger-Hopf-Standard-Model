from pathlib import Path

import sympy as sp

from bhsm.interface import action_selected_junction_functional as theorem


ROOT = Path(__file__).resolve().parents[1]


def test_repository_clifford_conventions():
    gn = theorem.gamma_n()
    gs = theorem.gamma_star()
    grading = theorem.collar_grading()
    assert gn**2 == sp.eye(2)
    assert gs**2 == sp.eye(2)
    assert gn * gs + gs * gn == sp.zeros(2)
    assert grading == sp.diag(-1, 1)
    assert grading**2 == sp.eye(2)


def test_trace_map_and_inner_product_are_declared():
    trace = theorem.trace_ledger()
    assert trace["trace_map"].startswith("T_J:")
    assert "sqrt(|gamma|)" in trace["measure"]
    assert "u^dagger v" in trace["inner_product"]
    assert trace["bulk_orthogonality_implies_trace_orthogonality"] is False


def test_orientation_reversal_tracks_green_form():
    trace = theorem.trace_ledger()
    assert "n->-n" in trace["orientation"]
    assert theorem.green_form_matrix() == sp.diag(1, -1)
    assert theorem.gamma_n() == theorem.gamma_n().T.conjugate()


def test_existing_geometry_has_no_joint_or_corner():
    geometry = theorem.geometry_ledger()
    assert geometry["boundary_count"] == 1
    assert geometry["intersecting_boundary_pieces"] is False
    assert geometry["codimension_two_corner"] is False
    assert geometry["joint_angle_eta"] is None
    assert geometry["required_Hayward_joint_term"] is False


def test_GHY_is_required_but_not_physical_tension():
    geometry = theorem.geometry_ledger()
    assert geometry["GHY_coefficient"].startswith("fixed")
    assert "not tension" in geometry["GHY_classification"]


def test_moving_endpoint_does_not_create_second_face():
    geometry = theorem.geometry_ledger()
    assert geometry["moving_endpoint"] is True
    assert "does not create a second boundary face" in geometry["moving_endpoint_status"]


def test_induced_measure_and_shape_variations_are_recorded():
    bending = theorem.bending_ledger()
    assert bending["induced_measure_variation"].startswith("delta dmu_J")
    assert "Delta_Sigma" in bending["shape_variation"]
    assert "Ric(n,n)" in bending["shape_variation"]


def test_no_duplicate_invariant():
    assert theorem.no_duplicate_invariants()
    ids = [row["id"] for row in theorem.invariant_ledger()]
    assert len(ids) == len(set(ids))


def test_triality_representation_is_exact_C3():
    cycle = theorem.triality_cycle()
    assert cycle == sp.Matrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    assert cycle**3 == sp.eye(3)
    assert cycle.T * cycle == sp.eye(3)


def test_exact_Hermitian_commutant_basis():
    cycle = theorem.triality_cycle()
    basis = theorem.triality_commutant_basis()
    assert len(basis) == 3
    assert all(item == item.T.conjugate() for item in basis)
    assert all(item * cycle == cycle * item for item in basis)
    assert sp.Matrix.hstack(*(sp.Matrix(item).reshape(9, 1) for item in basis)).rank() == 3


def test_general_commutant_solves_equations():
    matrix = theorem.triality_commutant()
    assert theorem.commutant_equations_hold(matrix)
    assert matrix == matrix.T.conjugate()


def test_commutant_is_circulant_not_arbitrary_matrix():
    matrix = theorem.triality_commutant()
    assert matrix[0, 0] == matrix[1, 1] == matrix[2, 2]
    assert matrix[1, 0] == matrix[2, 1] == matrix[0, 2]
    assert matrix[0, 1] == matrix[1, 2] == matrix[2, 0]
    assert theorem.artifact_payloads()["invariants"]["triality"]["real_coefficient_count"] == 3


def test_fourier_diagonalization_and_eigenvalues():
    fourier = theorem.triality_fourier()
    matrix = theorem.triality_commutant()
    diagonal = sp.simplify(fourier.T.conjugate() * matrix * fourier)
    assert diagonal == sp.diag(*theorem.triality_eigenvalues())


def test_generic_eigenvalue_multiplicity_is_three_singlets():
    triality = theorem.artifact_payloads()["invariants"]["triality"]
    assert triality["generic_multiplicities"] == [1, 1, 1]
    assert triality["nonuniversal_response_permitted"] is True
    assert triality["nonuniversal_response_required"] is False


def test_scalar_subalgebra_is_recovered():
    assert theorem.triality_commutant().subs({theorem.X: 0, theorem.Y: 0}) == theorem.A * sp.eye(3)


def test_all_present_terms_have_source_classification():
    rows = theorem.invariant_ledger()
    assert all("classification" in row and "coefficient_fixed" in row for row in rows)
    present = [row for row in rows if row["present"]]
    assert [row["id"] for row in present] == ["P1_GHY"]


def test_optional_matter_basis_uses_declared_clifford_structures():
    ids = {row["id"] for row in theorem.invariant_ledger() if row["sector"] == "fermionic"}
    assert ids == {"matter_scalar", "matter_normal", "matter_wall", "matter_grading"}
    assert all(
        row["required"] is False and row["coefficient_fixed"] is False
        for row in theorem.invariant_ledger()
        if row["sector"] == "fermionic"
    )


def test_green_form_maximal_isotropy_for_unitary_graph():
    u = theorem.cayley_unitary()
    vector = theorem.maximal_isotropic_trace(u)
    assert sp.simplify(u * sp.conjugate(u)) == 1
    assert theorem.green_flux(vector) == 0


def test_cayley_convention_is_derived_from_stated_graph_equation():
    u = theorem.cayley_unitary()
    assert sp.simplify((1 + sp.I * theorem.ALPHA) * u - (1 - sp.I * theorem.ALPHA)) == 0
    inverse = sp.simplify(sp.I * (u - 1) / (u + 1))
    assert inverse == theorem.ALPHA


def test_orientation_reversal_inverts_cayley_unitary():
    u = theorem.cayley_unitary(theorem.ALPHA)
    reversed_u = theorem.cayley_unitary(-theorem.ALPHA)
    assert sp.simplify(reversed_u - 1 / u) == 0


def test_current_action_selects_no_domain():
    domain = theorem.domain_ledger()
    assert domain["current_S_J_F"] == 0
    assert domain["unique_domain_selected"] is False
    assert domain["finite_family_selected"] is False
    assert domain["remaining_family"] == "U(1)"
    assert domain["result"] == theorem.DOMAIN_RESULT


def test_self_adjointness_and_flux_cancellation_are_family_wide():
    domain = theorem.domain_ledger()
    assert "every unitary U" in domain["flux_cancellation"]
    assert "every maximal-isotropic graph" in domain["self_adjointness"]
    assert domain["ellipticity"].startswith("not established")


def test_charge_triality_conjugation_and_index_compatibility():
    domain = theorem.domain_ledger()
    assert "Q_em" in domain["charge_preservation"]
    assert "Comm(C3)" in domain["triality_covariance"]
    assert domain["conjugation"] == "U maps to conjugate U"
    assert "does not select U" in domain["Callias_compatibility"]


def test_v6_7_mode_data_do_not_export_required_point_traces():
    trace = theorem.trace_ledger()
    assert trace["v6_7_zero_mode"]["point_trace"] is False
    assert trace["v6_7_first_heavy"]["point_trace"] is False
    assert trace["v6_7_first_heavy"]["normalized_eigenvector"] is False
    assert trace["trace_overlap_evaluable_for_optional_operator"] is False


def test_current_light_heavy_projection_uses_trace_and_is_zero():
    projection = theorem.projection_ledger()
    assert projection["definition"].startswith("j_01=(T_J f_0)^dagger")
    assert projection["bulk_overlap_substituted"] is False
    assert projection["current_j_01"] == 0
    assert projection["current_V_LH"] == "0_3"
    assert projection["zero_reason"] == "operator absence, not bulk L2 orthogonality"


def test_V_HL_is_adjoint_and_truncation_is_consistent():
    blocks = theorem.light_heavy_blocks()
    assert blocks["V_LH"] == sp.zeros(3)
    assert blocks["V_HL"] == blocks["V_LH"].T.conjugate()
    assert blocks["H_LL"] == theorem.P * sp.eye(3)
    assert blocks["H_HH"] == (theorem.P + theorem.M_H) * sp.eye(3)


def test_optional_projection_is_coefficient_dependent():
    optional = theorem.optional_junction_operator()
    assert optional == theorem.triality_commutant()
    assert theorem.commutant_equations_hold(optional)
    assert "not evaluable" in theorem.projection_ledger()["optional_trace_status"]


def test_parity_does_not_fake_operator_absence():
    projection = theorem.projection_ledger()
    assert projection["parity_forces_all_optional_terms_zero"] is False


def test_same_sector_clifford_operators_commute():
    h0 = theorem.kinetic_operator()
    assert theorem.commutator(h0, sp.eye(2)) == sp.zeros(2)
    assert theorem.commutator(h0, theorem.collar_grading()) == sp.zeros(2)


def test_mass_like_clifford_operators_anticommute():
    h0 = theorem.kinetic_operator()
    assert theorem.anticommutator(h0, theorem.gamma_n()) == sp.zeros(2)
    assert theorem.anticommutator(h0, theorem.gamma_star()) == sp.zeros(2)


def test_mass_like_squared_dispersion_is_conditional():
    squared = theorem.mass_like_squared_dispersion(theorem.ALPHA)
    assert squared == (theorem.P**2 + theorem.ALPHA**2) * sp.eye(2)
    ledger = theorem.dispersion_ledger()
    assert ledger["opposite_sector"]["conditional_dispersion"] == "E_i^2=p^2+mu_i"
    assert ledger["opposite_sector"]["status"].startswith("symmetry permitted")


def test_same_chirality_is_not_K_prop():
    ledger = theorem.dispersion_ledger()
    assert ledger["same_sector"]["K_prop"] is None
    assert "E^0" in ledger["same_sector"]["classification"]


def test_current_dispersion_has_no_forced_inverse_p_law():
    ledger = theorem.dispersion_ledger()
    assert ledger["current_operator"] == 0
    assert ledger["current_energy_shift"] == 0
    assert ledger["current_K_prop"] is None
    assert ledger["relative_neutral_phase"] == 0
    assert ledger["mass_squared_classification"] == "not generated"


def test_background_fermion_bilinear_has_no_tree_level_bending():
    bending = theorem.bending_ledger()
    assert bending["background_matter_state"] == "Psi_background=0"
    assert bending["fermion_quadratic_tree_level_bending"] == 0
    assert bending["fermion_loop_used"] is False


def test_formal_constraint_reduced_hessian_is_Hermitian():
    h_phys = theorem.constraint_reduced_hessian()
    assert h_phys == h_phys.T.conjugate()


def test_gauge_kernel_removed_before_constraint_inverse():
    bending = theorem.bending_ledger()
    assert bending["gauge_kernel"] == "must be removed before H_CC inversion"
    assert bending["H_phys_Hermitian"] is True


def test_k_b_and_sheet_bending_are_not_inserted():
    bending = theorem.bending_ledger()
    assert bending["k_b"] is None
    assert bending["B_plus"] is None
    assert bending["B_minus"] is None
    assert bending["lower_tachyon_certified"] is False
    assert bending["lower_ghost_certified"] is False


def test_exact_missing_bosonic_invariant_and_coefficient_are_named():
    bending = theorem.bending_ledger()
    assert bending["minimal_missing_bosonic_invariant"].startswith("S_J,bos^(0)=tau_J")
    assert bending["missing_coefficient"] == "tau_J"
    assert "not fixed by well-posedness" in bending["tau_J_status"]
    assert bending["result"] == theorem.BENDING_RESULT


def test_orientation_is_not_used_as_second_variation():
    assert theorem.bending_ledger()["orientation_sign_is_second_variation"] is False


def test_dependency_graph_does_not_merge_independent_primitives():
    graph = theorem.dependency_graph()
    assert graph["one_package_closes_all_targets"] is False
    assert graph["independent_primitives_remain"] == [
        "fermion junction coefficients",
        "tau_J",
    ]
    assert graph["structural_case"] == 7


def test_preserves_lambda_geom_and_v6_9_results():
    report = theorem.artifact_payloads()["report"]
    assert report["lambda_geom_universality_changed"] is False
    assert "BHSM_AVAILABLE_C_BHSM_HAS_ZERO_LIGHT_HEAVY_COUPLING" in report["preserved_results"]
    assert "BHSM_AUXILIARY_INDEX_ONE_CERTIFIED" in report["preserved_results"]


def test_no_measured_inputs_or_forbidden_new_physics():
    for payload in theorem.artifact_payloads().values():
        assert payload["measured_inputs_used"] is False
        assert payload["fitted_parameters_used"] is False
        assert payload["sector_dependent_coupling_introduced"] is False
        assert payload["physical_bulk_Dirac_parent_law_introduced"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_exactly_six_deterministic_artifacts():
    expected = theorem.artifact_bytes()
    assert len(expected) == 6
    assert set(expected) == set(theorem.ARTIFACT_FILES.values())
    assert all(content.endswith(b"\n") for content in expected.values())


def test_committed_artifacts_match_materializer():
    expected = theorem.artifact_bytes()
    actual = {
        filename: (ROOT / "artifacts" / filename).read_bytes()
        for filename in expected
    }
    assert actual == expected
