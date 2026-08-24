from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_n12_gate7_minimal_event_transport_scalar import build_payload


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_MINIMAL_EVENT_TRANSPORT_SCALAR_AUDIT.json"
)


def _record() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_minimal_transport_scalar_regenerates() -> None:
    record = _record()
    assert json.dumps(record, sort_keys=True) == json.dumps(
        build_payload(), sort_keys=True
    )
    assert record["validation_passed"] is True


def test_transport_is_split_before_norms() -> None:
    split = _record()["transport_split"]
    assert split["exact_transport_split"] == (
        "G(Y)=D_e_ord(Y)[V(Y)]=G0(Y)+Q(Y)"
    )
    assert split["minimal_acceleration_scalar"] == (
        "Q(Y)=alpha_Y(D(Y)^(-1)*b(Y))"
    )
    assert split["exterior_remainder"] == (
        "R_EXT(Y)=G0(Y)+<Q_PERP*alpha_Y^sharp,S(Y)*Q_PERP*b(Y)>"
    )


def test_three_representations_have_one_owner() -> None:
    representations = _record()["three_representation_adjudication"]
    assert list(representations) == [
        "1_adjoint",
        "2_bordered_Schur_and_mixed_resolvent",
        "3_action_jet",
    ]
    assert all(
        item["global_bound_or_sign_derived"] is False
        for item in representations.values()
    )
    assert representations["2_bordered_Schur_and_mixed_resolvent"][
        "continuum_Fredholm_determinant_claimed"
    ] is False


def test_exact_algebra_replay_agrees() -> None:
    replay = _record()["exact_algebra_replay"]
    assert replay["primal_Q"] == "2/5"
    assert replay["adjoint_Q"] == "2/5"
    assert replay["bordered_Schur_Q"] == "2/5"
    assert replay["bordered_determinant"] == "-2"
    assert replay["all_three_equal_exactly"] is True


def test_finite_hitting_discriminator_retains_infinite_branch() -> None:
    hitting = _record()["finite_hitting_adjudication"]
    assert hitting["power_law"]["phi(s)=c*s^p_with_p<1"] == (
        "FINITE_HITTING_FORCED"
    )
    assert "INTEGRAL_DIVERGES" in hitting["power_law"][
        "phi(s)=c*s^p_with_p>=1"
    ]
    assert hitting["retained_phi_certified"] is False
    assert hitting["infinite_regular_branch_eliminated"] is False
    assert hitting["existing_local_terminal_chart"][
        "finite_hitting_after_chart_entry_certified"
    ] is True
    assert hitting["existing_local_terminal_chart"][
        "current_child_chart_entry_certified"
    ] is False


def test_gate_and_chord_claim_boundaries_remain_closed() -> None:
    record = _record()
    assert record["Gate7_status_changed"] is False
    assert record["two_chord_global_promotion_authorized"] is False
    assert record["chord_03_proof_value_established"] is False
    assert record["chord_03_authorized"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_minimal_transport_scalar_artifact_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "83CA81A77EC8C3CD7AFD7302DA2A7F9240FF80E598A6F0C77895B8CF8C8DEFBD"
