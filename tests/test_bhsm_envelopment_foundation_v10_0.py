from __future__ import annotations

import numpy as np

from bhsm.interface.envelopment import foundation


def test_canonical_doctrine_is_structural_not_a_theorem():
    row = foundation.canonical_doctrine()
    assert row["classification"] == "STRUCTURAL_POSTULATE"
    assert row["canonical_repository_doctrine"] is True
    assert row["theorem_claimed"] is False
    assert row["hierarchy"] == ["cosmos", "environment", "envelopment", "sub-envelopment"]


def test_complete_state_and_relative_periodic_particle_definition():
    state = foundation.complete_state_definition()
    particle = foundation.particle_definition()
    assert state["bulk_v10_fields"] == ["G_AB", "chi", "sigma", "eta", "Lambda_eta"]
    assert "Phi(tau+T)=h.Phi(tau)" in particle["definition"]
    assert particle["rigid_fixed_radius_required"] is False
    assert "C3 family operation" in particle["allowed_h"]


def test_boundary_is_spectral_and_mass_uses_complete_stress():
    boundary = foundation.boundary_definition()
    mass = foundation.mass_definition()
    assert boundary["formation_gate"] == "lambda_min(H_sigma^(0)[Phi])=0"
    assert boundary["fixed_coordinate_boundary"] is False
    assert mass["local_arbitrary_mass_input"] is False
    assert mass["physical_mass_derived"] is False
    assert "gauge dressing" in mass["total_stress_requires"]


def test_cyclic_projectors_are_an_exact_rank_one_resolution():
    projectors = foundation.cyclic_projectors()
    assert len(projectors) == 3
    assert np.allclose(sum(projectors), np.eye(3), atol=1.0e-12)
    for index, projector in enumerate(projectors):
        assert np.allclose(projector @ projector, projector, atol=1.0e-12)
        assert np.allclose(projector.conj().T, projector, atol=1.0e-12)
        assert np.isclose(np.trace(projector), 1.0)
        for other_index, other in enumerate(projectors):
            if index != other_index:
                assert np.allclose(projector @ other, 0.0, atol=1.0e-12)


def test_frozen_ledgers_are_preserved_but_slot_intertwiner_is_open():
    row = foundation.generation_definition()
    assert row["frozen_ledgers"]["lepton"] == [[0, 0], [5, 2], [9, 3]]
    assert row["frozen_ledgers"]["up"] == [[0, 0], [6, 0], [10, 1]]
    assert row["frozen_ledgers"]["down"] == [[0, 0], [6, 3], [8, 2]]
    assert row["unique_projector_to_frozen_slot_correspondence"] is None


def test_foundation_payload_reaches_only_foundational_mark():
    payload = foundation.foundation_payload()
    assert payload["foundation_status"] == "REACHED"
    assert payload["validation_passed"] is True
    assert payload["physical_prediction_promoted"] is False
    assert payload["frozen_hierarchy"]["numerical_frozen_predictions_changed"] is False
