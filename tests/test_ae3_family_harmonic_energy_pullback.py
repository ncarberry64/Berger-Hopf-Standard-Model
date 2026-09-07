import hashlib

import numpy as np

from bhsm.interface.ae3_family_harmonic_energy_pullback import (
    claim_boundary,
    harmonic_spectral_pullback,
    physical_mass_ownership_gate,
    positive_energy_killer_test,
    pulled_back_operator,
)
from scripts.materialize_ae3_family_harmonic_energy_pullback import TARGET, build_payload, main


def test_pullback_of_distinct_harmonics_is_family_noncentral():
    operator = pulled_back_operator((0.0, 35.0, 99.0))
    assert np.allclose(operator, np.diag((0.0, 35.0, 99.0)))
    assert not np.allclose(operator, np.trace(operator) * np.eye(3) / 3.0)


def test_frozen_mode_eigenvalues_are_reproduced_without_a_spectrum_rebuild():
    result = harmonic_spectral_pullback()
    expected = {
        "charged_lepton": [0, 35, 99],
        "up": [0, 48, 120],
        "down": [0, 48, 80],
    }
    for sector, values in expected.items():
        actual = result["sectors"][sector]["dimensionless_R_F_squared_eigenvalues"]
        assert np.allclose(actual, values)
    assert result["spectral_noncentrality_derived"]
    assert not result["family_dependent_radius_present"]


def test_positive_monotone_energy_fails_the_frozen_family_ordering():
    result = positive_energy_killer_test()
    assert result["test_passed"]
    assert not result["monotone_positive_F_of_lambda_compatible_with_frozen_roles"]
    assert all(row["middle_over_heavy_displacement"] is None for row in result["rows"])
    assert all(not row["frozen_mass_order_compatible"] for row in result["rows"])


def test_scalar_stiffness_is_not_relabelled_as_a_fermion_mass():
    gate = physical_mass_ownership_gate()
    assert gate["Berger_scalar_eigenvalues_action_normalized"]
    assert not gate["parent_action_mode_energy_displacement_evaluated"]
    assert not gate["spinor_Dirac_lift_of_scalar_labels_constructed"]
    assert not gate["physical_mass_operator_derived"]
    assert not gate["old_exponential_overlap_rule_used"]


def test_claim_boundary_preserves_broader_candidate_without_overclaiming():
    boundary = claim_boundary()
    assert boundary["family_noncentral_spectral_stiffness_derived"]
    assert not boundary["family_mass_hierarchy_derived"]
    assert not boundary["broader_signed_or_nonmonotone_energy_mechanism_disproved"]


def test_materialized_audit_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
