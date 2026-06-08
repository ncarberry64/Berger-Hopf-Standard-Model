"""BHSM scalar-sector action scaffold."""

from __future__ import annotations

from dataclasses import dataclass


HIGGS_PROJECTED_LIGHT_MODE = "HIGGS_PROJECTED_LIGHT_MODE"
HOPF_GAP_LIFTED = "HOPF_GAP_LIFTED"
HT_COMPLEMENT_LIFTED = "HT_COMPLEMENT_LIFTED"
DERIVATIVE_SCREENED = "DERIVATIVE_SCREENED"
CURVATURE_SCREENED = "CURVATURE_SCREENED"
VIRTUAL_ONLY = "VIRTUAL_ONLY"
FORBIDDEN_UNSCREENED_LIGHT_SCALAR = "FORBIDDEN_UNSCREENED_LIGHT_SCALAR"
OPEN_SCALAR_RISK = "OPEN_SCALAR_RISK"


@dataclass(frozen=True)
class ScalarActionTerm:
    """One symbolic scalar-sector action term."""

    id: str
    expression: str
    channel: str
    preserves_single_higgs_projection: bool
    lifts_complement: bool
    screens_direct_coupling: bool
    forbids_unscreened_light_scalar: bool
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ScalarMode:
    """Action-level scalar/topographic mode row."""

    mode_id: str
    label: str
    channel: str
    effective_mass_gev: float | None
    coupling_to_matter: str
    derivative_screened: bool
    curvature_screened: bool
    virtual_only: bool
    on_shell_light_particle: bool
    status: str
    limitations: tuple[str, ...]


def scalar_action_terms() -> tuple[ScalarActionTerm, ...]:
    """Return symbolic scalar-sector action terms."""

    return (
        ScalarActionTerm(
            id="SA1",
            expression="|D_mu H_0|^2 - V(H_0)",
            channel=HIGGS_PROJECTED_LIGHT_MODE,
            preserves_single_higgs_projection=True,
            lifts_complement=False,
            screens_direct_coupling=False,
            forbids_unscreened_light_scalar=False,
            status="ACTION_SCAFFOLD",
            assumptions=("H(x,y)=H(x) Phi_0(y) is the unique light Higgs projection.",),
            limitations=("Uniqueness must be proven from the full scalar action.",),
        ),
        ScalarActionTerm(
            id="SA2",
            expression="m_perp^2 |Phi_perp|^2, m_perp >= 4*pi^2*v",
            channel=HOPF_GAP_LIFTED,
            preserves_single_higgs_projection=True,
            lifts_complement=True,
            screens_direct_coupling=True,
            forbids_unscreened_light_scalar=False,
            status="HOPF_GAP_SCAFFOLD",
            assumptions=("Orthogonal scalar complement satisfies the Hopf/H_T lift condition.",),
            limitations=("Full scalar spectrum remains open.",),
        ),
        ScalarActionTerm(
            id="SA3",
            expression="Phi_perp H_T Phi_perp",
            channel=HT_COMPLEMENT_LIFTED,
            preserves_single_higgs_projection=True,
            lifts_complement=True,
            screens_direct_coupling=True,
            forbids_unscreened_light_scalar=False,
            status="HT_FORMAL_KERNEL_LINKED",
            assumptions=("Uses corrected DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL scaffold, not coordinate-first H_T.",),
            limitations=("Full H_T theorem remains open.",),
        ),
        ScalarActionTerm(
            id="SA4",
            expression="(partial_mu T_loc)^2 / Lambda_T^2",
            channel=DERIVATIVE_SCREENED,
            preserves_single_higgs_projection=True,
            lifts_complement=False,
            screens_direct_coupling=True,
            forbids_unscreened_light_scalar=False,
            status="SCREENING_SCAFFOLD",
            assumptions=("Topographic mode couples through derivative-filtered channels.",),
            limitations=("Action-level derivative coupling proof remains open.",),
        ),
        ScalarActionTerm(
            id="SA5",
            expression="K[rho_Phi] T_loc^2",
            channel=CURVATURE_SCREENED,
            preserves_single_higgs_projection=True,
            lifts_complement=False,
            screens_direct_coupling=True,
            forbids_unscreened_light_scalar=False,
            status="SCREENING_SCAFFOLD",
            assumptions=("Curvature-filtered modes do not mediate unscreened fifth forces.",),
            limitations=("Curvature/profile proof remains open.",),
        ),
        ScalarActionTerm(
            id="SA6",
            expression="virtual/off-shell scalar-topographic exchange",
            channel=VIRTUAL_ONLY,
            preserves_single_higgs_projection=True,
            lifts_complement=False,
            screens_direct_coupling=True,
            forbids_unscreened_light_scalar=False,
            status="STATE_ONTOLOGY_LINKED",
            assumptions=("Virtual-only contributions are not on-shell light particles.",),
            limitations=("Ontology classification is not a full action proof.",),
        ),
        ScalarActionTerm(
            id="SA7",
            expression="g_phi psi_bar psi phi_light",
            channel=FORBIDDEN_UNSCREENED_LIGHT_SCALAR,
            preserves_single_higgs_projection=False,
            lifts_complement=False,
            screens_direct_coupling=False,
            forbids_unscreened_light_scalar=True,
            status="FALSIFIER_RULE",
            assumptions=("Unscreened direct-coupled light scalar is not allowed in the SM-equivalent low-energy limit.",),
            limitations=("If found in the full action, scalar decoupling fails or remains open risk.",),
        ),
    )


def action_level_scalar_modes() -> tuple[ScalarMode, ...]:
    """Return representative action-level scalar/topographic modes."""

    return (
        ScalarMode("higgs_projection", "H(x) Phi_0(y)", HIGGS_PROJECTED_LIGHT_MODE, None, "SM Higgs coupling", False, False, False, True, "ALLOWED_SM_HIGGS", ("The SM Higgs projection is the unique allowed light scalar.",)),
        ScalarMode("heavy_scalar_complement", "Phi_perp", HOPF_GAP_LIFTED, 4.0e4, "lifted/decoupled", False, False, False, False, "HEAVY_LIFTED_STATE", ("Mass is a scaffold scale representative.",)),
        ScalarMode("ht_scalar_complement", "Phi_perp|H_perp", HT_COMPLEMENT_LIFTED, 4.0e4, "lifted/decoupled", False, False, False, False, "HT_COMPLEMENT_LIFTED", ("Depends on corrected formal-kernel H_T scaffold.",)),
        ScalarMode("derivative_topographic", "T_der", DERIVATIVE_SCREENED, 100.0, "derivative-filtered", True, False, False, False, "DERIVATIVE_SCREENED_CONDITIONAL", ("Conditional until derivative coupling is action-proven.",)),
        ScalarMode("curvature_topographic", "T_curv", CURVATURE_SCREENED, 100.0, "curvature-filtered", False, True, False, False, "CURVATURE_SCREENED_CONDITIONAL", ("Conditional until curvature filter is action-proven.",)),
        ScalarMode("virtual_topographic", "T_virtual", VIRTUAL_ONLY, None, "virtual-only", False, False, True, False, "VIRTUAL_ONLY_NOT_PARTICLE", ("No on-shell mass/range is assigned to virtual-only mode.",)),
    )
