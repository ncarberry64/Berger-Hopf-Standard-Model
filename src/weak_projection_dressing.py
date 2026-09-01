"""Weak-doublet projection scaffold for BHSM virtual dressing."""

from __future__ import annotations

from dataclasses import dataclass

from mode_selection import hopf_charge, omega_up


WEAK_PROJECTION_LINKED = "WEAK_PROJECTION_LINKED"


@dataclass(frozen=True)
class WeakProjectionDressingStep:
    """One internal step for the Z_virt^{u,2}=1/2 dressing scaffold."""

    id: str
    statement: str
    passes: bool
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


def weak_projection_factor_for_middle_up() -> float:
    """Return the weak-doublet probability projection factor."""

    return 0.5


def weak_projection_dressing_steps() -> tuple[WeakProjectionDressingStep, ...]:
    """Return internal weak-projection dressing steps."""

    mode = (6, 0)
    q = hopf_charge(*mode)
    omega = omega_up(*mode)
    return (
        WeakProjectionDressingStep(
            id="WP1",
            statement="middle up mode is pure-fiber with j=0",
            passes=mode[1] == 0,
            evidence=("mode=(6,0)", "j=0"),
            limitations=("This identifies the scope; it does not derive a loop amplitude.",),
        ),
        WeakProjectionDressingStep(
            id="WP2",
            statement="middle up mode satisfies q=6 and Omega_u=6",
            passes=q == 6 and omega == 6,
            evidence=(f"q={q}", f"Omega_u={omega}"),
            limitations=("Boundary-functional linkage is inherited from v1.2.",),
        ),
        WeakProjectionDressingStep(
            id="WP3",
            statement="weak-doublet probability projection supplies factor 1/2",
            passes=weak_projection_factor_for_middle_up() == 0.5,
            evidence=("two weak components projected to one mode-local channel",),
            limitations=("Full virtual-environment loop derivation remains open.",),
        ),
    )

