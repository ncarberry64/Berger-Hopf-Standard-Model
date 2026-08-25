from scripts.derive_n12_compact_operator_reset_lift_fiber_invariance import (
    build_payload,
)


def test_reset_lift_kernel_is_operator_invariant() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    geometry = payload["linearized_geometry"]
    assert geometry["reset_lift_kernel_dimension"] == 66
    assert geometry["child_projection_rank"] == 73
    assert geometry["lifted_kernel_reset_residual_norm"] < 1.0e-12


def test_lift_invariance_does_not_remove_common_scale() -> None:
    payload = build_payload()
    domain = payload["reduced_force_domain"]
    assert domain["physical_common_scale"] == "RETAINED"
    assert payload["claim_boundary"]["full_child_projection_force"].startswith(
        "OPEN"
    )
