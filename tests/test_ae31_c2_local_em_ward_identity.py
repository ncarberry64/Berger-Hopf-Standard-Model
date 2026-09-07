import hashlib

import pytest

from bhsm.interface.ae31_c2_local_em_ward_identity import (
    charged_lepton_qem_ledger,
    local_em_claim_boundary,
    local_ward_identity_witness,
    pauli_transversality_witness,
)
from scripts.materialize_ae31_c2_local_em_ward_identity import (
    TARGET,
    build_payload,
    main,
)


def test_physical_charged_lepton_chiralities_have_same_qem_charge():
    result = charged_lepton_qem_ledger()
    assert result["left_component"]["Q_em"] == -1.0
    assert result["left_handed_conjugate_ledger_component"]["Q_em"] == 1.0
    assert result["physical_right_component"]["Q_em"] == -1.0
    assert result["mass_endomorphism_commutes_with_Qem"]
    assert result["current_C2_source_domain_attached"]
    assert not result["photon_normalization_used"]


def test_local_three_family_ward_takahashi_identity_is_exact():
    result = local_ward_identity_witness()
    assert result["Clifford_residual"] < 1.0e-12
    assert result["mass_charge_commutator_residual"] < 1.0e-12
    assert result["Ward_Takahashi_residual"] < 1.0e-12
    assert result["same_identity_for_all_three_family_projectors"]
    assert not result["measured_mass_used"]
    assert not result["canonical_photon_residue_used"]
    with pytest.raises(ValueError):
        local_ward_identity_witness(momentum=(1.0, 2.0), transfer=(0.0,) * 4)


def test_pauli_form_factor_is_transverse_and_not_fixed_by_ward_identity():
    result = pauli_transversality_witness()
    assert result["antisymmetry_residual"] < 1.0e-12
    assert result["q_sigma_q_residual"] < 1.0e-12
    assert result["Ward_identity_constrains_longitudinal_vertex"]
    assert not result["Ward_identity_determines_F2"]
    assert result["minimal_tree_vertex_F2"] == 0.0
    assert not result["tree_F2_is_quantum_muon_anomaly"]


def test_claim_boundary_keeps_photon_and_muon_observables_open():
    result = local_em_claim_boundary()
    assert result["CURRENT_C2_LOCAL_TREE_WARD_TAKAHASHI_IDENTITY_DERIVED"]
    assert result["CURRENT_C2_PAULI_FORM_FACTOR_TRANSVERSALITY_DERIVED"]
    assert result["CURRENT_C2_MINIMAL_TREE_F2_ZERO_DERIVED"]
    assert not result["CURRENT_C2_PHYSICAL_PHOTON_POLE_DERIVED"]
    assert not result["CURRENT_C2_RENORMALIZED_MUON_VERTEX_DERIVED"]
    assert not result["MUON_MAGNETIC_MOMENT_DERIVED"]


def test_artifact_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
