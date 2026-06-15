from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_gate import (  # noqa: E402
    BareYukawaParameters,
    S_bare,
    Y_bare,
    fiber_fraction,
    lambda_hat,
)


def test_heavy_reference_normalization() -> None:
    params = BareYukawaParameters(epsilon=0.02, tau0=0.2, beta_eff=0.01, xi=1.0)
    assert S_bare(0, 0, params) == 0.0
    assert Y_bare(0, 0, params) == 1.0


def test_lambda_hat_nonnegative_and_fiber_fraction_range() -> None:
    for q in range(0, 10):
        for j in range(0, 6):
            lam = lambda_hat(q, j, epsilon=0.05)
            fraction = fiber_fraction(q, j)
            assert lam >= 0.0
            assert 0.0 <= fraction <= 1.0
    assert fiber_fraction(0, 0) == 0.0
    assert fiber_fraction(6, 0) == 1.0


def test_xi_zero_nonnegative_beta_action_increases_with_lambda_hat() -> None:
    params = BareYukawaParameters(epsilon=0.0, tau0=0.1, beta_eff=0.01, xi=0.0)
    samples = [(1, 0), (1, 1), (2, 1), (3, 2), (5, 2)]
    ordered = sorted(samples, key=lambda item: lambda_hat(item[0], item[1], params.epsilon))
    actions = [S_bare(q, j, params) for q, j in ordered]
    assert actions == sorted(actions)


def test_y_bare_is_exponential_of_negative_action() -> None:
    params = BareYukawaParameters(epsilon=0.01, tau0=0.15, beta_eff=0.005, xi=0.2)
    action = S_bare(3, 3, params)
    assert math.isclose(Y_bare(3, 3, params), math.exp(-action), rel_tol=0.0, abs_tol=1e-15)
