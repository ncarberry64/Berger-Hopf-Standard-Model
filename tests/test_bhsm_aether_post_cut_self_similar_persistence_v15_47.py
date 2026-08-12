import json

from bhsm.interface import aether_post_cut_self_similar_persistence_v15_47 as persistence


def test_self_similar_constraint_matches_reconstructed_slice():
    result = persistence.self_similar_reduction(points=500)
    assert result["initial_constraint_identity_residual"] < 3e-10
    assert result["initial_G"] > 0.0


def test_self_similar_sector_has_no_periodic_orbit():
    result = persistence.self_similar_reduction(points=500)
    assert result["minimum_G"] > 0.0
    assert result["sampled_minimum_G"] > 0.0
    assert result["turning_point_count"] == 0
    assert result["self_similar_periodic_orbit_exists"] is False


def test_payload_is_deterministic_and_selects_nonround_flow(tmp_path):
    payload = persistence.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["self_similar_sector_decided"] is True
    assert payload["claim_boundary"]["persistent_particle_derived"] is False
    path = persistence.materialize(tmp_path)
    assert json.loads(path.read_text(encoding="utf-8"))["validation_passed"] is True
    assert path.read_text(encoding="utf-8") == persistence.deterministic_json(payload)

