from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_ACCEPTED_REPLAY_CENTER_OUTWARD_74D_CONTRACTION.json"
DATA = RESULT.with_suffix(".npz")
SCRIPT = ROOT / "scripts" / "certify_n12_gate7_accepted_replay_center_outward_74d.py"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".py", ".json", ".md"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_accepted_center_directional_curvature_is_proof_amplified() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    operands = record["outward_operands"]
    assert record["status"] == (
        "SAME_CENTER_GATE7_Z2_PROOF_COORDINATE_AMPLIFICATION_ADJUDICATED"
    )
    assert record["decision"]["classification"] == (
        "PROOF_COORDINATE_CURVATURE_AMPLIFICATION"
    )
    assert record["decision"]["current_same_center_contraction_theorem_obstructed"] is True
    assert record["decision"]["physical_spacetime_instability_claim"] is False
    assert record["decision"]["root_nonexistence_claim"] is False
    assert record["theorem_convention"] == {
        "self_map": "Y+Z1*r+Z2*r^2<r",
        "contraction": "Z1+2*Z2*r<1",
    }
    assert operands["Y_owner_node"] == 300
    assert operands["Z2_obstruction_node"] == 1
    assert operands["Z2_obstruction_causal_coordinate"] == 61
    assert 0.0 < operands["Y_lower"] <= operands["Y_upper"]
    assert operands["Y_upper"] - operands["Y_lower"] < 3.0e-21
    assert 3.0e6 < operands["Z2_required_lower_from_center_direction"]
    assert (
        operands["Z2_required_lower_from_center_direction"]
        <= operands["Z2_same_direction_upper"]
    )

    getcontext().prec = 80
    y = Decimal(str(operands["Y_lower"]))
    z2 = Decimal(str(operands["Z2_required_lower_from_center_direction"]))
    discriminant = Decimal(1) - Decimal(4) * y * z2
    minimum = y - Decimal(1) / (Decimal(4) * z2)
    assert discriminant < 0
    assert minimum > 0
    assert Decimal(str(
        operands["necessary_discriminant_upper_1_minus_4_Ylower_Z2lower"]
    )) < 0
    assert Decimal(str(
        operands["necessary_quadratic_global_minimum_lower"]
    )) > 0
    assert record["validation_passed"] is True
    assert all(record["validation"].values())
    assert record["FULL_BHSM_COMPLETE"] is False

    location = record["Z2_WITNESS_LOCATION"]
    assert location["owning_block_intervals"] == [0, 1]
    assert location["owning_node"] == 1
    assert location["witness_action_arc_coordinate"] == 0.25
    assert location["classification"] == "PRE_ENVELOPMENT"
    assert location["signed_action_separation_witness_minus_first_hit"][1] < 0.0

    amplification = record["amplification_decomposition"]
    assert amplification["field_plus_descriptor_identity_verified"] is True
    assert amplification["input_direction_descriptor_component"] == 0.0
    assert amplification["descriptor_test_scaling_amplification_lower"] > 9.9e5
    assert amplification["descriptor_preconditioner_amplification_lower"] > 10.0
    assert amplification["descriptor_causal_transport_amplification_lower"] > 300.0
    assert amplification["terminal_descriptor_output_only"]["lower"] > 4.0e6
    assert amplification["terminal_field_output_only"]["upper"] < 7.0e5
    assert amplification["local_preconditioned_radii_discriminant"] > 0.0
    assert (
        operands["required_radius_floor"]
        < amplification["local_preconditioned_small_root"]
        < operands["frozen_domain_radius_ceiling"]
    )
    assert record["formation_corridor_adjudication"]["theorem_scope"] == (
        "A_ROOT_SOLUTION_ONLY_THROUGH_FIRST_HIT"
    )
    assert record["child_persistence_separation"]["separately_owned_in_BHSM"] is True


def test_directional_obstruction_data_and_frozen_provenance() -> None:
    record = json.loads(RESULT.read_text(encoding="utf-8"))
    with np.load(DATA) as source:
        midpoint = np.asarray(
            source["terminal_directional_curvature_mid"], dtype=float,
        )
        radius = np.asarray(
            source["terminal_directional_curvature_radius"], dtype=float,
        )
        field_midpoint = np.asarray(
            source["terminal_field_output_directional_curvature_mid"],
            dtype=float,
        )
        descriptor_midpoint = np.asarray(
            source["terminal_descriptor_output_directional_curvature_mid"],
            dtype=float,
        )
        assert midpoint.shape == radius.shape == (74,)
        assert field_midpoint.shape == descriptor_midpoint.shape == (74,)
        assert np.allclose(
            field_midpoint + descriptor_midpoint, midpoint,
            rtol=2.0e-10, atol=5.0e-5,
        )
        assert np.all(np.isfinite(midpoint))
        assert np.all(np.isfinite(radius))
        assert np.all(radius >= 0.0)
        assert np.array_equal(source["local_interval_indices"], [0, 1])
        assert int(source["obstruction_node"]) == 1
        assert int(source["obstruction_causal_coordinate"]) == 61
        magnitude_lower = np.linalg.norm(
            np.maximum(np.abs(midpoint) - radius, 0.0),
        )
        assert magnitude_lower >= record["outward_operands"][
            "Z2_required_lower_from_center_direction"
        ]

    provenance = record["provenance_SHA256"]
    assert provenance[
        "scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py"
    ] == _sha256(SCRIPT)
    assert provenance[
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz"
    ] == "3E52E013B473938B6959D5D63054FCC4D5057A13A71D10E2874ADB9A53E85B4E"
    assert provenance[
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_MIDPOINT_REPLAY.npz"
    ] == "B47F9C415CF9A7A3D7EB1888A245FB7C66EB11879E70F84202B7E3A557CF2988"
    assert len(record["derived_work_aggregate_SHA256"]) == 4
    assert all(
        len(value) == 64
        for value in record["derived_work_aggregate_SHA256"].values()
    )


def test_certificate_uses_outward_backend_without_jax_authority() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "from flint import arb, arb_mat, ctx" in text
    assert "def _rate_second_directional(" in text
    assert "signed D3/D4/D5 action" in text
    assert "import jax" not in text
    assert "--curvature-obstruction" in text
