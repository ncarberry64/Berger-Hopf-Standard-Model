from fractions import Fraction
from math import isclose

from bhsm.interface.completion.manual_campaign_recovery_v14_83 import (
    CANONICAL_BUNDLE_AGGREGATE_SHA256,
    CANONICAL_BUNDLE_COUNT,
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
    area_landau_coefficients,
    bundle_aggregate_sha256,
    completion_payload,
    dtn_shape_quartic,
    materialize,
    radial_core_softening_identity,
)


def test_download_lineage_is_hash_locked_and_steering_jumps_are_recorded() -> None:
    payload = completion_payload()
    provenance = payload["bundle_provenance"]
    assert provenance["canonical_bundle_count"] == CANONICAL_BUNDLE_COUNT == 49
    assert bundle_aggregate_sha256() == CANONICAL_BUNDLE_AGGREGATE_SHA256
    assert provenance["steering_only_version_jumps"] == ["v14.78", "v14.80"]
    assert provenance["duplicate_v14_48"] == "BYTE_IDENTICAL_EXCLUDED"


def test_round_area_landau_coefficients_are_independently_reconstructed() -> None:
    assert area_landau_coefficients() == {
        "r": Fraction(5, 3),
        "u": Fraction(-83, 15),
        "v": Fraction(43, 30),
        "three_u_plus_v": Fraction(-91, 6),
    }


def test_dtn_shape_quartic_has_the_claimed_exact_threshold() -> None:
    thin = dtn_shape_quartic(1.0, 0.5)
    thick = dtn_shape_quartic(1.0, 2.0)
    assert thin["sign"] == "POSITIVE"
    assert thick["sign"] == "NEGATIVE"
    assert isclose(float(thin["threshold_qL"]), 1.1462158347805889)


def test_core_softening_threshold_is_exactly_one_third() -> None:
    below = radial_core_softening_identity(0.2, 1.0, 2.0, 3.0)
    above = radial_core_softening_identity(0.5, 1.0, 2.0, 3.0)
    reverse = radial_core_softening_identity(0.5, -1.0, 2.0, 3.0)
    assert below["softens"] is False
    assert above["softens"] is True
    assert reverse["softens"] is False


def test_recovery_fails_closed_at_all_provenance_gates(tmp_path) -> None:
    payload = completion_payload()
    status = payload["completion_status"]
    assert payload["validation_passed"] is True
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["open_gates"]["charged_current_kernel"] == CHARGED_CURRENT_PROVENANCE_GATE
    assert payload["open_gates"]["noncentral_left_handed_current"] == NONCENTRAL_CURRENT_GATE
    assert status["BHSM_complete"] is False
    assert status["Mark_III"] == "NOT_REACHED"
    assert status["USB_synchronization_eligible"] is False
    assert payload["frozen_predictions_changed"] is False
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second

