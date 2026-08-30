import numpy as np
import pytest

from bhsm.interface.universal_rg_flow import (
    ActionBetaFunction,
    RGInvariant,
    integrate_joint_rg_flow,
)


def test_joint_one_loop_kinetic_residue_transport_matches_closed_form() -> None:
    coefficients = np.asarray([41.0 / 6.0, -19.0 / 6.0, -7.0])
    beta = ActionBetaFunction(
        parameter_ids=("K_U1", "K_SU2", "K_SU3"),
        evaluate=lambda _log_scale, _values: -coefficients / (8.0 * np.pi**2),
        action_version="BHSM-TEST",
        scheme_id="common-heat-scheme",
        provenance=("same graded loop ledger",),
        derived_from_same_action_ledger=True,
    )
    initial = np.asarray([5.0 / 3.0, 1.0, 1.0])
    result = integrate_joint_rg_flow(beta, initial, 1.0, 2.0)
    expected = initial - coefficients * np.log(2.0) / (8.0 * np.pi**2)
    np.testing.assert_allclose(result.values[:, -1], expected, rtol=2.0e-13, atol=2.0e-13)
    result.require_promotable()


def test_action_identity_is_monitored_over_whole_joint_flow() -> None:
    beta = ActionBetaFunction(
        parameter_ids=("a", "b"),
        evaluate=lambda _log_scale, values: np.asarray([values[1], -values[0]]),
        action_version="BHSM-TEST",
        scheme_id="common",
        provenance=("same action",),
        derived_from_same_action_ledger=True,
    )
    invariant = RGInvariant(
        "unit-circle",
        lambda values: np.asarray([values @ values - 1.0]),
        ("Ward identity",),
    )
    result = integrate_joint_rg_flow(beta, np.asarray([1.0, 0.0]), 1.0, 3.0, [invariant])
    assert result.maximum_invariant_residual < 5.0e-10
    result.require_promotable(tolerance=5.0e-10)


def test_split_or_fitted_beta_source_is_rejected() -> None:
    with pytest.raises(ValueError, match="same-action"):
        ActionBetaFunction(
            parameter_ids=("gauge-only",),
            evaluate=lambda _scale, values: values,
            action_version="BHSM-TEST",
            scheme_id="split",
            provenance=("sector fit",),
            derived_from_same_action_ledger=False,
        )
