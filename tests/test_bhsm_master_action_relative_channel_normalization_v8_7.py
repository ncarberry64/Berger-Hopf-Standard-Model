import numpy as np

from bhsm.interface.master_action import relative_channel_normalization as v87


def test_c3_characters_are_orthonormal():
    assert np.allclose(v87.c3_character_gram(), np.eye(3), atol=1e-13)


def test_point_character_identity():
    result = v87.point_character_identity()
    assert result["verified"]
    assert result["residual_frobenius"] < 1e-12


def test_parent_pushforward_equal_norm():
    result = v87.parent_orthonormal_pushforward()
    assert result["orthonormal"]
    assert result["relative_modulus_chi1_over_chi0"] == 1.0


def test_g2_ratio_is_unit_modulus_minus_i():
    result = v87.canonical_relative_ratio()
    assert result["formula"] == "c_chi1/c_chi0=-i"
    assert result["modulus"] == 1.0


def test_master_action_does_not_attach_physical_ratio():
    result = v87.physical_action_attachment_audit()
    assert not result["common_parent_current_term_present"]
    assert not result["physical_relative_channel_ratio_selected"]


def test_canonical_candidate_not_promoted():
    result = v87.normalized_candidate_audit()
    assert not result["passes_frozen_ten_percent_gate"]


def test_payload_passes():
    result = v87.payload()
    assert result["validation_passed"]
    assert not result["physical_CKM_promoted"]
    assert not result["frozen_predictions_changed"]

