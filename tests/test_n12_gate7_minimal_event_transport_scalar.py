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


def test_uniform_scale_does_not_force_pole_dominance() -> None:
    weights = _record()["uniform_scale_transport_weight_audit"]
    assert weights["Euler_Dirac_block_D_weight"] == 7
    assert weights["Euler_Dirac_source_b_weight"] == 7
    assert weights["acceleration_D_inverse_b_weight"] == 0
    assert weights["minimal_acceleration_scalar_Q_weight"] == 7
    assert weights["pole_term_c_psi_b_psi_over_e_ord_weight"] == 7
    assert weights["exterior_remainder_R_EXT_weight"] == 7
    assert weights["pole_has_strict_scale_advantage_over_exterior_remainder"] is False
    assert weights["large_uniform_scale_forces_transport_sign"] is False


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


def test_existing_witness_excludes_strict_negative_transport_from_reset() -> None:
    witness = _record()["existing_witness_transport_adjudication"]
    assert witness["endpoint_delta_at_96"] > 0.0
    assert witness["endpoint_secant_rate_at_96"] > 0.0
    assert witness["endpoint_move_away_cross_quadrature_robust"] is True
    assert witness[
        "strict_negative_transport_from_reset_compatible_with_endpoints"
    ] is False
    assert witness["interior_or_later_return_adjudicated"] is False


def test_gate_and_chord_claim_boundaries_remain_closed() -> None:
    record = _record()
    assert record["Gate7_status_changed"] is False
    assert record["two_chord_global_promotion_authorized"] is False
    assert record["chord_03_proof_value_established"] is False
    assert record["chord_03_authorized"] is False
    assert record["FULL_BHSM_COMPLETE"] is False


def test_minimal_transport_scalar_artifact_is_content_addressable() -> None:
    digest = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest().upper()
    assert digest == "1CF578073FC4FF2C1D89BD7D717CB94F0F52AD9159B484E5C459D9EEBAF4E2BC"
