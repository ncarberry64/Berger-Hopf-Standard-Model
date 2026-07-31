from __future__ import annotations

from bhsm.interface.master_action import (
    geometry_only_geon_fr_carrier_completion as v91,
)


def test_configuration_space_is_exactly_typed_and_framed():
    row = v91.configuration_space_definition()
    assert row["spacetime"] == "M8=I_t x S7"
    assert row["canonical_spatial_manifold"].startswith("Sigma=S7")
    assert row["spin_structure"].startswith("unique")
    assert "s>9/2" in row["regularity"]["metrics"]
    assert "(0,fr)" in row["gauge_group"]
    assert row["large_diffeomorphisms_quotiented"] is False
    assert row["topology_change_allowed"] is False


def test_full_ansatz_moduli_and_collective_spaces_are_not_conflated():
    rows = v91.configuration_space_strata()
    assert len(rows) == 6
    assert rows[1]["space"] == "small-diffeomorphism quotient Q_geom^0"
    assert "cannot determine" in rows[3]["topology_use"]
    assert "undefined" in rows[-1]["topology_use"]


def test_small_diffeomorphism_quotient_has_no_order_two_fr_loop():
    row = v91.small_diffeomorphism_pi1_theorem()
    assert row["total_space_contractible"]
    assert row["action_free"]
    assert row["pi1_Q_geom_0"] == "0"
    assert row["nontrivial_order_two_loop"] is False
    assert row["nontrivial_FR_character"] is None
    assert row["FR_line_bundle"] is None


def test_large_diffeomorphism_z2_is_not_misidentified_as_rotation_exchange():
    row = v91.large_diffeomorphism_audit()
    assert row["orientation_preserving_mapping_class_group"].endswith("Z2")
    assert row["belongs_to_small_diff_quotient"] is False
    assert row["identified_with_two_pi_rotation"] is False
    assert row["identified_with_geon_exchange"] is False
    assert row["action_selects_between_characters"] is False
    assert row["local_spinor_bundle_produced"] is False


def test_prior_v66_mapping_space_result_is_preserved_but_not_promoted():
    row = v91.prior_fr_reconciliation()
    assert row["v6_6_pi1"] == "pi4(S3)=Z2"
    assert row["equal_to_Q_geom_0"] is False
    assert row["action_derived_map_from_Q_geom_0_to_v6_6_space"] is None
    assert row["promotion_in_v9_1"] is False


def test_all_requested_loop_candidates_are_classified():
    rows = v91.candidate_loop_ledger()
    assert len(rows) == 9
    by_name = {row["candidate"]: row for row in rows}
    assert by_name["2pi spatial rotation"]["order"] == 1
    assert by_name["Spin(8) triality permutation"]["order"] == 3
    assert by_name["connected-sum or handle geon"]["closed_in_Q_geom_0"] is False


def test_metric_does_not_naturally_select_g2_or_triality_projectors():
    row = v91.g2_selection_no_go()
    assert row["compatible_G2_fiber_for_fixed_metric_orientation"] == "SO(7)/G2=RP7"
    assert row["metric_selects_unique_point"] is False
    assert row["torsion_free_G2_on_S7"] is False
    assert "H^3(S7)=0" in row["torsion_free_topology_reason"]
    assert all(
        row[key] is None
        for key in ("eta_phi", "J_u", "Pi_10", "P_chi0", "P_chi1", "P_chi2")
    )


def test_fr_sign_line_cannot_masquerade_as_local_chiral_carrier():
    row = v91.local_carrier_no_go()
    assert row["local_spacetime_bundle"] is None
    assert row["Spin_1_3_Clifford_action"] is None
    assert row["left_right_chirality_operator"] is None
    assert row["configuration_to_M4_transgression"] is None


def test_topology_report_is_fail_closed_and_input_clean():
    report = v91.topology_status_report()
    assert report["validation_passed"]
    assert report["final_verdict"] == v91.FINAL_VERDICT
    assert report["physical_promotion"] is False
    assert report["measured_flavor_data_used"] is False
    assert report["new_fundamental_fermion_added"] is False
    assert report["frozen_predictions_changed"] is False

