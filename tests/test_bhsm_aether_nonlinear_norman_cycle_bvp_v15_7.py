from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from bhsm.interface.aether_nonlinear_norman_cycle_bvp_v15_7 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    PRIMARY_VERDICT,
    artifact_payloads,
    cavitation_seed_eligibility,
    complete_noether_ledger_payload,
    continuation_eligibility,
    de_envelopment_receiving_domain_payload,
    deterministic_json,
    floquet_reconstruction_payload,
    formation_continuation_payload,
    full_completion_payload,
    master_reclosure_payload,
    materialize,
    physical_tangent_monodromy_payload,
    public_repository_sync_payload,
    relative_periodic_persistence_payload,
    unknown_state_domain_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_full_bhsm_completion_is_false() -> None:
    assert FULL_BHSM_COMPLETE is False
    assert full_completion_payload()["FULL_BHSM_COMPLETE"] is False


def test_exactly_one_first_missing_object_is_declared() -> None:
    payload = full_completion_payload()
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["Hindsight_20_20"]["OPEN"] == [EXACT_NEXT_OBJECT]


def test_parent_state_is_m8_and_does_not_smuggle_intrinsic_m4_fields() -> None:
    payload = unknown_state_domain_payload()
    assert "sigma" in payload["parent_state_variables"]
    assert payload["intrinsic_M4_fields_not_smuggled_into_M8_state"] == ["A_SM", "Psi_SM"]


def test_bvp_fails_before_continuation() -> None:
    payload = unknown_state_domain_payload()
    assert payload["BVP_well_posed"] is False
    assert payload["unique_parent_surface"] == "Sigma_A"
    assert payload["localized_incoming_packet_W_in"] is None
    assert payload["first_missing_object"] == EXACT_NEXT_OBJECT


def test_general_hessian_is_conditional_not_realized_threshold() -> None:
    payload = formation_continuation_payload()
    assert payload["threshold_problem_well_defined_conditionally"] is True
    assert payload["localized_packet_action_derived"] is False
    assert payload["simple_zero_crossing_proved"] is False


def test_lyapunov_schmidt_is_not_started_without_gate_data() -> None:
    payload = formation_continuation_payload()
    assert payload["Lyapunov_Schmidt_reduction_allowed"] is False
    assert payload["nonlinear_formation_map"] == "UNDEFINED_NO_ACTION_DERIVED_LOCALIZED_CAVITATION_PACKET"


def test_unique_parent_surface_is_ontology_not_selection_problem() -> None:
    payload = unknown_state_domain_payload()
    assert payload["multiple_parent_surface_selection_required"] is False
    assert payload["unique_parent_surface_status"] == "AUTHOR_ONTOLOGY_PHYSICAL_MECHANISM_TARGET"
    assert payload["unique_does_not_mean_static"] is True


def test_w_in_is_diagnostic_not_a_new_field() -> None:
    payload = unknown_state_domain_payload()
    assert payload["packet_is_new_primitive_field"] is False
    assert payload["new_fields"] == []


@pytest.mark.parametrize("missing", range(6))
def test_every_cavitation_seed_condition_is_required(missing: int) -> None:
    gates = [True] * 6
    gates[missing] = False
    assert cavitation_seed_eligibility(
        packet_action_derived=gates[0],
        constraints_solved=gates[1],
        localized=gates[2],
        finite_action_or_norm=gates[3],
        common_domain_time_preserved=gates[4],
        physical_zero_crossing=gates[5],
    ) is False


def test_complete_cavitation_seed_is_eligible_for_continuation() -> None:
    assert cavitation_seed_eligibility(
        packet_action_derived=True,
        constraints_solved=True,
        localized=True,
        finite_action_or_norm=True,
        common_domain_time_preserved=True,
        physical_zero_crossing=True,
    ) is True


@pytest.mark.parametrize(
    ("background", "domain", "kernel", "transverse", "expected"),
    [
        (False, True, 1, True, False),
        (True, False, 1, True, False),
        (True, True, None, True, False),
        (True, True, 2, True, False),
        (True, True, 1, False, False),
        (True, True, 1, True, True),
    ],
)
def test_continuation_eligibility_is_fail_closed(
    background: bool, domain: bool, kernel: int | None, transverse: bool, expected: bool
) -> None:
    assert continuation_eligibility(
        background_selected=background,
        domain_selected=domain,
        kernel_dimension=kernel,
        transversality_nonzero=transverse,
    ) is expected


def test_negative_kernel_dimension_is_rejected() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        continuation_eligibility(
            background_selected=True,
            domain_selected=True,
            kernel_dimension=-1,
            transversality_nonzero=True,
        )


def test_v14_93_radial_no_bifurcation_is_preserved_locally() -> None:
    radial = formation_continuation_payload()["radial_v14_93"]
    assert radial["cubic_coefficient"] == 0
    assert radial["quartic_coefficient"].endswith("> 0")
    assert radial["nearby_equivariant_radial_bifurcation"] is False
    assert radial["classification"] == "ZERO_MODE_WITHOUT_CAVITATION"


def test_v14_93_is_not_promoted_to_global_no_go() -> None:
    radial = formation_continuation_payload()["radial_v14_93"]
    assert radial["scope"] == "LOCAL_EQUIVARIANT_RADIAL_SECTOR_ONLY"
    assert radial["global_no_go"] is False


def test_persistence_is_not_reached() -> None:
    payload = relative_periodic_persistence_payload()
    assert payload["physical_persistent_orbit"] == "NOT_REACHED_FORMATION_GATE"
    assert payload["action_selected_orbit"] is None


def test_no_branch_is_selected_numerically() -> None:
    assert relative_periodic_persistence_payload()["branch_selected_by_numerical_convenience"] is False


def test_de_envelopment_remains_forward_not_inverse_or_dagger() -> None:
    payload = de_envelopment_receiving_domain_payload()
    assert payload["equals_formation_inverse"] is False
    assert payload["equals_formation_dagger"] is False
    assert "updated_parent" in payload["map_type"]


def test_receiving_domain_and_trigger_are_unowned() -> None:
    payload = de_envelopment_receiving_domain_payload()
    assert payload["receiving_domain"] is None
    assert payload["trigger"] is None
    assert payload["status"] == "NOT_REACHED_AND_UNOWNED"


def test_noether_ledger_is_incomplete() -> None:
    payload = complete_noether_ledger_payload()
    assert payload["ledger_complete"] is False
    assert payload["orphan_free_transfer_proved"] is False


def test_physical_monodromy_and_spectrum_are_undefined() -> None:
    payload = physical_tangent_monodromy_payload()
    assert payload["monodromy_operator"] is None
    assert payload["physical_loop_spectrum"] is None


def test_floquet_log_branch_is_not_arbitrarily_selected() -> None:
    payload = floquet_reconstruction_payload()
    assert payload["logarithm_branch_selected"] is False
    assert payload["reconstruction"] is None


def test_master_counts_remain_undefined() -> None:
    payload = master_reclosure_payload()
    assert payload["physical_master_solution_count"] == "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"
    assert payload["gauge_quotiented_master_solution_count"] == "UNDEFINED_MISSING_UPSTREAM_STRUCTURE"


def test_scale_flavor_and_encapsulation_stay_open() -> None:
    payload = master_reclosure_payload()
    assert payload["absolute_scale"] == "OPEN"
    assert payload["CKM"].startswith("OPEN")
    assert payload["PMNS"].startswith("OPEN")
    assert payload["encapsulation_event"].startswith("OPEN")


def test_integrity_firewalls() -> None:
    payload = full_completion_payload()
    for key in (
        "empirical_inputs_added",
        "fitted_parameters_added",
        "arbitrary_continuous_parameters_added",
        "preferred_frame_added",
        "frozen_predictions_changed",
        "official_prediction_logic_changed",
        "USB_TOUCHED",
    ):
        assert payload[key] is False


def test_hindsight_has_required_sections() -> None:
    assert set(full_completion_payload()["Hindsight_20_20"]) == {
        "VALIDATED", "INVALIDATED", "RECLASSIFIED", "OPEN"
    }


def test_primary_verdict_is_embedded() -> None:
    assert full_completion_payload()["primary_verdict"] == PRIMARY_VERDICT


def test_ten_nonempty_artifacts_are_declared() -> None:
    payloads = artifact_payloads()
    assert len(payloads) == 10
    assert all(payload and payload.get("artifact") for payload in payloads.values())


def test_json_is_strict_and_newline_terminated() -> None:
    encoded = deterministic_json(full_completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded
    assert json.loads(encoded)["version"] == "v15.7"


def test_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    first = materialize(tmp_path / "a")
    second = materialize(tmp_path / "b")
    assert [p.name for p in first] == [p.name for p in second]
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in first] == [
        hashlib.sha256(p.read_bytes()).hexdigest() for p in second
    ]


def test_committed_artifacts_match_materializer(tmp_path: Path) -> None:
    generated = materialize(tmp_path)
    for path in generated:
        assert path.read_bytes() == (ROOT / "artifacts" / path.name).read_bytes()


def test_public_sync_payload_is_current_and_usb_safe() -> None:
    payload = public_repository_sync_payload()
    assert payload["current_public_version"] == "v15.7"
    assert payload["stale_current_status_hits"] == 0
    assert payload["broken_current_links"] == 0
    assert payload["USB_TOUCHED"] is False
