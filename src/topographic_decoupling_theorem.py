"""Topographic decoupling theorem compatibility wrapper."""

from __future__ import annotations

from scalar_full_action_theorem import (
    ScalarFullActionTheoremReport,
    build_scalar_full_action_theorem_report,
)


def build_topographic_decoupling_theorem_report() -> ScalarFullActionTheoremReport:
    """Return the scalar/topographic decoupling theorem status.

    The current topographic decoupling theorem status is identical to the
    scalar full-action status: scaffold-passing, but full action proof open.
    """

    return build_scalar_full_action_theorem_report()

