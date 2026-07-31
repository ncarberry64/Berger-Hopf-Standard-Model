from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.master_action import (
    eight_dimensional_vacuum_flavor_completion as v90,
)


ROOT = Path(__file__).resolve().parents[1]


def test_all_manual_sprints_are_integrated_with_fail_closed_dispositions():
    rows = v90.integration_matrix()
    assert [row["sprint"] for row in rows] == [
        "v8.4",
        "v8.5",
        "v8.6",
        "v8.7",
        "v8.8",
        "v8.9",
    ]
    assert all("INTEGRATED" in row["disposition"] for row in rows)
    assert all((ROOT / row["source"]).is_file() for row in rows)
    assert all((ROOT / row["test"]).is_file() for row in rows)


def test_static_round_product_vacuum_is_rejected_with_scoped_claim():
    audit = v90.homogeneous_static_product_no_go()
    assert audit["finite_radius_solution"] is False
    assert "not all" in audit["scope"]


def test_scalar_target_does_not_fabricate_fr_quantization():
    audit = v90.scalar_topology_audit()
    assert audit["target_contractible"]
    assert audit["pi_7_of_scalar_target"] == 0
    assert audit["FR_sector_from_scalar_maps_alone"] is False


def test_two_independent_proxy_numerical_routes_agree_without_promotion():
    vacuum = v90.vacuum_proxy_crosscheck()
    lens = v90.lens_numerical_crosscheck()
    assert vacuum["all_methods_agree"]
    assert lens["methods_agree"]
    assert vacuum["classification"] == "PROXY_STRESS_TEST_ONLY"
    assert lens["classification"] == "PROXY_STRESS_TEST_ONLY"
    assert vacuum["physical_promotion"] is False
    assert lens["physical_promotion"] is False


def test_physical_forms_and_matrix_fail_closed():
    forms = v90.physical_pullback_forms()
    assert all(
        forms[key] is None
        for key in ("G_u", "Q_u", "G_d", "Q_d", "K_ud", "V_BHSM")
    )
    assert forms["physical_matrix_promoted"] is False


def test_v90_status_passes_without_flavor_overclaim():
    report = v90.status_report()
    assert report["validation_passed"]
    assert report["physical_matrix_promoted"] is False
    assert report["measured_flavor_data_used"] is False
    assert report["new_fundamental_fermion_added"] is False
    assert report["frozen_predictions_changed"] is False
    assert report["final_verdict"] == v90.FINAL_VERDICT


def test_completion_gate_tracks_v90_obstruction():
    gate = v90.completion_gate_payload()
    assert gate["version"] == "v9.0"
    assert gate["current_verdict"] == v90.FINAL_VERDICT
    assert gate["next_highest_upstream_blocker"] == v90.NEXT_MISSING_OBJECT
    assert gate["BHSM_1_0_release_complete"] is False


def test_materializer_is_byte_idempotent(tmp_path):
    first_paths = v90.materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = v90.materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    campaign = json.loads(
        (tmp_path / "artifacts" / f"{v90.ARTIFACT_NAME}.json").read_text(
            encoding="utf-8"
        )
    )
    assert campaign["physical_pullback_forms"]["V_BHSM"] is None
