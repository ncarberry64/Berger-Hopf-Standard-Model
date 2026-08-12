import json

from bhsm.interface.aether_coupled_event_cycle_pushforward_v15_78 import (
    completion_payload,
    cycle_pushforward_contract,
    deterministic_json,
    simple_legendre_event_balance,
)


def test_backreaction_is_toward_event_and_integrability_threshold_is_exact():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert all(row["V_star"] < 0.0 for row in payload["backreaction_rows"])
    assert all(
        row["dV_star_d_epsilon"] > 0.0
        for row in payload["backreaction_rows"]
    )
    balance = simple_legendre_event_balance()
    assert balance["mass_impulse_integrable_iff"] == "p<2"
    assert balance["Yukawa_vertex_integrable_iff"] == "p<4/3"
    assert balance["gauge_residue_integrable"]
    assert balance["p_equals_4_over_7_not_assumed"]


def test_one_cycle_functional_owns_both_normalizations():
    contract = cycle_pushforward_contract()
    assert contract["same_parent_functional_for_gauge_and_Yukawa"]
    assert not contract["independent_normalization_conditions"]
    assert "Gamma_cycle" in contract["absolute_gauge_normalization"]
    assert "Gamma_cycle" in contract["left_right_vertex"]


def test_payload_is_deterministic_json():
    first = deterministic_json(completion_payload())
    second = deterministic_json(completion_payload())
    assert first == second
    assert json.loads(first)["version"] == "v15.78"
