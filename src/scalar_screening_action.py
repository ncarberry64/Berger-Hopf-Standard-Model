"""BHSM v1.6 scalar/topographic screening action scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from curvature_screening import curvature_screening_conditions
from derivative_screening import derivative_screening_conditions
from scalar_action import (
    CURVATURE_SCREENED,
    DERIVATIVE_SCREENED,
    FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
    HIGGS_PROJECTED_LIGHT_MODE,
    HOPF_GAP_LIFTED,
    HT_COMPLEMENT_LIFTED,
    OPEN_SCALAR_RISK,
    VIRTUAL_ONLY,
    ScalarMode,
    action_level_scalar_modes,
)


SCREENING_SCAFFOLD_PASSES = "SCREENING_SCAFFOLD_PASSES"
FIFTH_FORCE_EXCLUDED_CONDITIONALLY = "FIFTH_FORCE_EXCLUDED_CONDITIONALLY"
OPEN_SCALAR_RISK_STATUS = OPEN_SCALAR_RISK
FAILS_SCREENING = "FAILS_SCREENING"
FULL_SCREENING_THEOREM_PROVEN = "FULL_SCREENING_THEOREM_PROVEN"


@dataclass(frozen=True)
class ScreeningActionTerm:
    """One scalar/topographic screening term in the action scaffold."""

    id: str
    channel: str
    operator: str
    excludes_static_fifth_force: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class MatterCouplingRule:
    """Matter-coupling classification for one v1.5 scalar/topographic mode."""

    mode_id: str
    channel: str
    direct_matter_coupling: bool
    derivative_coupling_only: bool
    curvature_coupling_only: bool
    virtual_only: bool
    heavy_lifted: bool
    higgs_projected_sm_scalar: bool
    forbidden_unscreened_light_coupling: bool
    open_coupling_risk: bool
    ordinary_on_shell_fifth_force_mediator: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def screening_action_terms() -> tuple[ScreeningActionTerm, ...]:
    """Return symbolic screening action terms."""

    return (
        ScreeningActionTerm(
            id="ST1",
            channel=DERIVATIVE_SCREENED,
            operator="L_int ~ (1/M_*) partial_mu phi J^mu_topo",
            excludes_static_fifth_force=True,
            status="DERIVATIVE_SCREENING_DERIVED",
            assumptions=tuple(item.assumptions[0] for item in derivative_screening_conditions()),
            limitations=("Suppression scale and global absence of direct couplings remain open.",),
        ),
        ScreeningActionTerm(
            id="ST2",
            channel=CURVATURE_SCREENED,
            operator="L_int ~ phi R_topo",
            excludes_static_fifth_force=True,
            status="CURVATURE_SCREENING_DERIVED",
            assumptions=tuple(item.assumptions[0] for item in curvature_screening_conditions()),
            limitations=("Curvature-source uniqueness must be proven in the full action.",),
        ),
        ScreeningActionTerm(
            id="ST3",
            channel=VIRTUAL_ONLY,
            operator="off-shell scalar/topographic exchange",
            excludes_static_fifth_force=True,
            status=FIFTH_FORCE_EXCLUDED_CONDITIONALLY,
            assumptions=("Virtual-only modes are not on-shell ordinary fifth-force mediators.",),
            limitations=("Path-integral/off-shell proof remains scaffold-level.",),
        ),
        ScreeningActionTerm(
            id="ST4",
            channel=FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
            operator="g_phi psi_bar psi phi_light",
            excludes_static_fifth_force=False,
            status="FALSIFIER_RULE",
            assumptions=("Direct unscreened light scalar matter coupling is forbidden in the SM-equivalent limit.",),
            limitations=("If this term is present in the complete action, screening fails or remains open risk.",),
        ),
    )


def matter_coupling_rule_for_mode(mode: ScalarMode) -> MatterCouplingRule:
    """Classify one scalar/topographic mode against v1.6 screening rules."""

    heavy = mode.channel in {HOPF_GAP_LIFTED, HT_COMPLEMENT_LIFTED}
    higgs = mode.channel == HIGGS_PROJECTED_LIGHT_MODE
    derivative = mode.channel == DERIVATIVE_SCREENED and mode.derivative_screened
    curvature = mode.channel == CURVATURE_SCREENED and mode.curvature_screened
    virtual = mode.channel == VIRTUAL_ONLY and mode.virtual_only
    forbidden = mode.channel == FORBIDDEN_UNSCREENED_LIGHT_SCALAR
    open_risk = mode.channel == OPEN_SCALAR_RISK
    direct = higgs or forbidden or open_risk
    ordinary_mediator = bool(forbidden or open_risk)
    if higgs:
        status = "SM_HIGGS_ALLOWED"
    elif heavy:
        status = "FIFTH_FORCE_EXCLUDED_BY_MASS_GAP"
    elif derivative:
        status = "DERIVATIVE_SCREENED_NOT_STATIC_MEDIATOR"
    elif curvature:
        status = "CURVATURE_SCREENED_FLAT_LIMIT_SUPPRESSED"
    elif virtual:
        status = "VIRTUAL_ONLY_NOT_ON_SHELL_MEDIATOR"
    elif forbidden:
        status = FORBIDDEN_UNSCREENED_LIGHT_SCALAR
    else:
        status = OPEN_SCALAR_RISK
        open_risk = True
        ordinary_mediator = True
    return MatterCouplingRule(
        mode_id=mode.mode_id,
        channel=mode.channel,
        direct_matter_coupling=direct,
        derivative_coupling_only=derivative,
        curvature_coupling_only=curvature,
        virtual_only=virtual,
        heavy_lifted=heavy,
        higgs_projected_sm_scalar=higgs,
        forbidden_unscreened_light_coupling=forbidden,
        open_coupling_risk=open_risk,
        ordinary_on_shell_fifth_force_mediator=ordinary_mediator,
        status=status,
        assumptions=(
            "Classification is inherited from the v1.5 scalar action channel.",
            "No empirical residuals or flavor outputs are used.",
        ),
        limitations=(
            "Matter-coupling exclusion remains a scaffold until derived from the complete action.",
        ),
    )


def matter_coupling_audit(modes: tuple[ScalarMode, ...] | None = None) -> tuple[MatterCouplingRule, ...]:
    """Return matter-coupling audit rows for all v1.5 scalar modes."""

    scalar_modes = action_level_scalar_modes() if modes is None else modes
    return tuple(matter_coupling_rule_for_mode(mode) for mode in scalar_modes)

