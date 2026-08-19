from bhsm.interface.aether_n6_n12_nonlinear_homotopy_integrability_v21_36 import (
    nonlinear_homotopy_integrability_audit,
)


def test_nonlinear_homotopy_integrability_fails_closed_at_missing_map():
    audit = nonlinear_homotopy_integrability_audit()

    assert audit["validation_passed"] is True
    assert audit["linear_supporting_lemma"]["status"] == "VALIDATED_UNCHANGED"
    assert audit["source_audit"]["nonlinear_F_t_Y_implemented"] is False
    assert audit["endpoint_evidence"][
        "original_matched_N6_first_omitted_weak_H_minus_1_tail"
    ] > 0.0
    assert audit["endpoint_evidence"][
        "repaired_ordered_event_N6_first_omitted_weak_H_minus_1_tail"
    ] > 0.0
    assert audit["radii_cover_status"][
        "overlapping_nonlinear_segment_balls_meaningfully_defined"
    ] is False
    assert audit["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert audit["Q_XI_READOUT_UNLOCKED"] is False
    assert audit["FULL_BHSM_COMPLETE"] is False


def test_tail_anchor_provenance_is_not_conflated():
    evidence = nonlinear_homotopy_integrability_audit()["endpoint_evidence"]

    assert abs(
        evidence["original_matched_N6_first_omitted_weak_H_minus_1_tail"]
        - 0.086772051123605
    ) < 1.0e-14
    assert abs(
        evidence[
            "repaired_ordered_event_N6_first_omitted_weak_H_minus_1_tail"
        ]
        - 0.080655518582802
    ) < 1.0e-14
