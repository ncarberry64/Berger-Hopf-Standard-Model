import numpy as np

from bhsm.interface.aether_n3_terminal_joint_pushforward_v16_09 import (
    common_event_residues,
    completion_payload,
    terminal_soft_event,
)


def test_terminal_event_solves_constraints_zero_mode_and_spin_stress():
    event = terminal_soft_event()
    assert event["success"]
    assert event["maximum_constraint_residual"] < 2.0e-9
    assert abs(event["lambda_soft"]) < 2.0e-9
    assert event["rank16_spin_stress_projection_g_s"] != 0.0


def test_underresolved_terminal_event_is_rejected_before_gauge_lr():
    row = common_event_residues()
    assert row["minimum_eta_Legendre"] < 0.0
    assert not row["common_event_layer_admissible"]
    assert not row["gauge_DtN_and_LR_crossing_accepted"]
    assert not row["independent_gauge_or_Yukawa_normalization"]


def test_domain_exit_convergence_payload_passes():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert not payload["domain_exit_convergence"][
        "Euler_Dirac_soft_event_before_domain_exit"
    ]
