from __future__ import annotations

from bhsm.interface.completion.matter_sourced_spin4_multipole_v14_40 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    completion_payload,
    diagonal_density_allowed_r,
    family_source_payload,
    materialize,
    rigid_eta_rotor_source_payload,
    sector_graph_connected,
    supported_edges,
    wilson_source_payload,
)


def test_rigid_eta_rotor_is_L1_only() -> None:
    payload = rigid_eta_rotor_source_payload()
    assert payload["validation_passed"]
    assert payload["angular_character"]["L"] == 1
    assert payload["validation"]["L2_absent"]
    assert payload["validation"]["L3_absent"]


def test_diagonal_family_density_has_only_r0() -> None:
    assert diagonal_density_allowed_r() == (0,)


def test_diagonal_occupations_do_not_connect_either_sector() -> None:
    edges = supported_edges(diagonal_density_allowed_r())
    assert not sector_graph_connected("up", edges)
    assert not sector_graph_connected("down", edges)


def test_only_down_heavy_middle_edge_is_supported() -> None:
    payload = family_source_payload()
    supported = payload["supported_edges_from_diagonal_occupations"]
    assert len(supported) == 1
    assert supported[0]["sector"] == "down"
    assert supported[0]["source_slot"] == "heavy"
    assert supported[0]["target_slot"] == "middle"
    assert supported[0]["r"] == 0


def test_required_nonzero_r_edges_need_coherence() -> None:
    payload = family_source_payload()
    entries = payload["required_coherences"]
    required = [
        item
        for sector in ("up", "down")
        for item in entries[sector]
        if item["coherence_required"]
    ]
    assert {item["required_magnetic_transfer"] for item in required} == {1, 2, 3}


def test_static_Wilson_source_is_not_the_universal_L2_L3_source() -> None:
    payload = wilson_source_payload()
    assert payload["validation_passed"]
    assert payload["static_limit"]["coexact_L2_L3_source"] == 0
    assert payload["validation"]["state_dependent_backreaction_is_not_universal_CKM"]


def test_completion_gate_fails_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["validation"]["physical_CKM_not_emitted"]
    assert payload["validation"]["BHSM_not_complete"]


def test_materialization_is_deterministic(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
