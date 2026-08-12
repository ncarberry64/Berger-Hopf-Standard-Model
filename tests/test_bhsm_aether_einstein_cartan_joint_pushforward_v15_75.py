from bhsm.interface.aether_einstein_cartan_joint_pushforward_v15_75 import (
    completion_payload,
    forced_joint_crossing,
    lr_fierz_projection,
    quadratic_shell_divergence,
)


def test_contorsion_has_nonzero_lr_projection() -> None:
    projection = lr_fierz_projection()
    assert projection["nonzero_LR_projection"]
    assert not projection["elementary_Higgs_required"]


def test_shell_divergence_forces_crossing() -> None:
    assert quadratic_shell_divergence()["EC_kernel_limit"].startswith("+infinity")
    crossing = forced_joint_crossing()
    assert crossing["crossing_exists"]
    assert not crossing["independent_gauge_normalization"]
    assert not crossing["independent_Yukawa_coupling"]


def test_payload_validates() -> None:
    assert completion_payload()["validation_passed"]
