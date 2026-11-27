"""Classify the owner-authorized BHSM encapsulation interface action.

Norman P. Carberry authorizes one new physical primitive: an action for the
work by which an initiating event mode envelops its local spacetime
environment.  The authorization fixes the role and arguments of the action,
not its constitutive density.  This module derives the maximal covariant
first-order class, its formal variation, and the remaining freedom without
choosing response functions, fitted coefficients, a carrier, or a reset map.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Sequence

import numpy as np

from bhsm.interface.encapsulation_response_representation_theorem import (
    canonical_structure_ledger,
    constraint_noether_ledger,
    input_space_contract,
    output_space_contract,
    scale_and_control_ledger,
)
from bhsm.interface.environmental_child_compatibility_selection import (
    minimal_environmental_state_descriptor,
    scale_and_energy_variables,
)


ACTION_VERSION = "BHSM-AE-3.2.15-OWNER-AUTHORIZED-ENCAPSULATION-INTERFACE-ACTION"
CLASSIFICATION = "OWNER_AUTHORIZED_INTERFACE_ACTION_CLASS_DERIVED_VALUE_UNSELECTED"
DERIVATIVE_CLASS = "ORD1"
INTERFACE_FREEDOM_CLASS = "IF5"
UNIQUE_ACTUALIZATION_CLASS = "UA5"
LOOP_CLASS = "LOOP3"
EXACT_NEXT_OBJECT = (
    "ACTION_LEVEL_CONSTITUTIVE_ENVELOPMENT_WORK_DENSITY_OR_EQUIVALENT_"
    "FUNCTIONAL_SELECTION_PRINCIPLE_FIXING_THE_IF5_RESPONSE_FUNCTIONS_"
    "WITHOUT_FITTED_INTERFACE_PARAMETERS"
)


@dataclass(frozen=True)
class InvariantDensity:
    family: str
    representative: str
    covariance: str
    derivative_order: int
    status: str
    restriction: str


@dataclass(frozen=True)
class DensityCandidate:
    name: str
    derivative_order: int
    scalar_density: bool
    gauge_invariant: bool
    brst_compatible: bool
    spin_covariant: bool
    orientation_fr_compatible: bool
    event_mode_conditioned: bool
    environment_scale_conditioned: bool
    independent_fitted_parameters: bool = False
    child_coefficients_as_controls: bool = False
    passive_mismatch_only: bool = False
    duplicates_owned_ghy_or_bulk_term: bool = False


def owner_authorization() -> dict[str, Any]:
    """Record the new authority without retroactively changing the old action."""

    return {
        "authority": "NORMAN_P_CARBERRY_OWNER_AUTHORIZATION_2026_09_06",
        "new_primitive": "P-A*",
        "physical_meaning": (
            "physical work/process by which the initiating event mode envelops "
            "its local spacetime environment"
        ),
        "must_determine": ["iota_enc", "F_B", "L_s", "Delta_enc"],
        "strength_controls": ["M_event", "E_s", "Lambda_s"],
        "independently_fitted_interface_parameters_allowed": False,
        "part_of_previous_13_term_action": False,
        "mathematical_density_selected_by_authorization": False,
    }


def interface_variable_contract() -> dict[str, Any]:
    """Type all dynamical interface variables and their regularity."""

    return {
        "carrier": {
            "abstract_object": (
                "one compact oriented stratified carrier Sigma_enc with regular "
                "pieces Sigma_enc^(s), rather than unrelated event/child surfaces"
            ),
            "event_child_copies": "Sigma_e and Sigma_c are two trace copies of the same abstract carrier",
            "embeddings": (
                "iota_enc=(iota_e,iota_c), iota_e:Sigma_enc->M_event^(s), "
                "iota_c:Sigma_enc->M_child^(s)"
            ),
            "dimension": (
                "dim Sigma_enc^(s)=dim M^(s)-1 on regular hypersurface pieces; "
                "codimension-two corners are boundaries of those pieces, not a second carrier law"
            ),
            "active_strata": ["regular M8 pieces", "regular M5+ and M5- pieces", "regular M4 pieces"],
            "pregeometry_guardrail": "no ordinary embedded carrier is asserted inside C_A",
            "orientation": (
                "event outward conormal n_e and child outward conormal n_c are opposite "
                "under the retained orientation-preserving attachment"
            ),
            "normal_structure": "unit normal where the induced metric is non-null; conormal density otherwise",
            "regularity": (
                "H^(s+1) embeddings and attachment maps with s>(dim Sigma)/2+1, "
                "or smooth representatives; enough for traces, D F_B, normals, and first shape variation"
            ),
            "topology": "degree, incidence, spin lift, FR parity, and bundle class are frozen superselection data",
            "stratum": "stratum-preserving unless an independently owned transition vertex exists",
            "varied": True,
        },
        "attachment": {
            "map": "F_B:Sigma_e->Sigma_c",
            "class": "orientation-preserving H^(s+1) Diff-plus-spin/bundle lifts on each compatible regular piece",
            "transport": "C_s(F_B):Q_child,s->Q_event,s with cotangent adjoint C_s(F_B)^*",
            "variation": "eta_c=delta F_B o F_B^(-1)",
            "not_external_input": True,
        },
        "boundary_relation": {
            "object": "L_s in Gamma(Lag(T_s)) for each nonfermion reduced trace symplectic bundle T_s",
            "meaning": "a Lagrangian relation/subbundle, not an arbitrary matrix",
            "variation": "ell_s in T_(L_s) Lag(T_s), including constraint and BRST-compatible directions only",
            "fermion_scope": "AE2 fermion graph remains separately owned and is not re-fitted",
            "not_external_input": True,
        },
        "fields": {
            "event": "X_e with trace q_e=Gamma_e X_e and sector canonical covector Pi_e",
            "child": "X_c with trace q_c=Gamma_c X_c and sector canonical covector Pi_c",
            "sectors": ["geometry", "scalar/topographic", "gauge", "fermion", "ghost/BRST", "higher-spin"],
            "varied": True,
        },
    }


def control_state_contract() -> dict[str, Any]:
    """Separate variables, controls, and superselection data."""

    environment = minimal_environmental_state_descriptor()
    controls = input_space_contract()
    return {
        "control_state": "Xi_enc=(M_event,E_s,Lambda_s)",
        "dynamical_variables": ["X_e", "X_c", "iota_e", "iota_c", "F_B", "{L_s}"],
        "control_environment_data": {
            "M_event": {
                "owned_core": "initiating event state/eigenline, real chart amplitude, forward orientation, represented charges and geometry where defined",
                "phase": "included only if a gauge-invariant relative phase is selected; no arbitrary phase control",
                "polarization": "included only through an owned basis-invariant projector; frozen labels are not physical projectors",
            },
            "E_s": environment["formula"],
            "E_s_components": environment["components"],
            "Lambda_s": controls["scalar_controls"]["Lambda_s"],
        },
        "frozen_superselection_data": [
            "stratum alpha_s", "event type tau_s", "degree", "orientation", "FR parity",
            "incidence class", "Spin x G_SM bundle class", "family representation class",
        ],
        "forbidden_controls": [
            "independent child-mode coefficients", "fitted interface thresholds",
            "arbitrary harmonic amplitudes or phases", "measured particle outputs",
        ],
        "not_one_global_vector_space": controls["exact_current_mathematical_class"],
    }


def symmetry_contract() -> dict[str, Any]:
    return {
        "required": [
            "diagonal admissible stratum-preserving spatial diffeomorphisms",
            "G_SM bundle gauge covariance",
            "BRST compatibility on gauge-longitudinal and ghost blocks",
            "earned spin lifts",
            "orientation and FR parity covariance",
            "incidence and projector intertwining when the projectors exist",
            "equivariance under the actual stabilizer Stab(M_event,E_s,Sigma_enc) once selected",
        ],
        "not_assumed": [
            "full Diff across incompatible strata", "full Spin(4) on every carrier",
            "a physical actual stabilizer before the carrier is selected",
            "basis-dependent mode covariance inside degenerate eigenspaces",
        ],
        "action_value": "real, ghost-number zero, Grassmann even, and dimensionless in hbar=1 units",
    }


def invariant_density_ledger() -> list[dict[str, Any]]:
    """List the exhaustive invariant families at local order at most one."""

    rows = (
        InvariantDensity(
            "canonical_generating",
            "real invariant contractions of q_e, C(F_B)q_c, Pi_e, C(F_B)^(-*)Pi_c, and L_s",
            "scalar under diagonal carrier diffeomorphisms and invariant on the reduced bundle",
            0,
            "ALLOWED",
            "must not be mismatch-only if it is to generate nonzero active Delta_enc",
        ),
        InvariantDensity(
            "event_mode_source",
            "basis-invariant bilinears and higher invariant contractions of M_event with matched interface sectors",
            "only singlets in Hom_Gx(M_event,target) survive",
            0,
            "ALLOWED_CONDITIONALLY",
            "amplitudes, phase, and polarization must already be owned",
        ),
        InvariantDensity(
            "environment_cauchy_noether",
            "normal/tangential contractions of B_s with induced metric, conormal, traces, and canonical covectors",
            "tensor/covector density contraction on regular geometric strata",
            0,
            "ALLOWED",
            "no unique scalar energy-to-spacetime contraction is currently selected",
        ),
        InvariantDensity(
            "scale",
            "dimensionless functions of R_reset/ell_kappa, x_s, and dimensionless event/environment invariants",
            "scalar under every retained symmetry",
            0,
            "ALLOWED",
            "ell_kappa supplies dimensions but does not select the function",
        ),
        InvariantDensity(
            "attachment_first_jet",
            "invariant contractions of D F_B, induced metrics/coframes, Jacobian density, and lifted connection transport",
            "natural pullback under admissible diffeomorphisms and gauge/spin lifts",
            1,
            "REQUIRED_CLASS",
            "needed for connection transport and the first moving-domain variation",
        ),
        InvariantDensity(
            "carrier_first_jet",
            "induced metric, volume density, normal/conormal, and first embedding derivatives",
            "geometric scalar density on each regular carrier piece",
            1,
            "REQUIRED_CLASS",
            "enough for first shape work without adding new curvature dynamics",
        ),
        InvariantDensity(
            "field_first_jet",
            "tangential covariant derivatives and owned normal canonical/Green data",
            "gauge/spin covariant and BRST compatible",
            1,
            "ALLOWED_CONDITIONALLY",
            "only where the sector operator domain already defines the derivative",
        ),
        InvariantDensity(
            "gauge_spin_scalar",
            "Tr(F_parallel^2), invariant scalar/topographic contractions, Grassmann-even spinor bilinears, and BRST-closed ghost pairs",
            "G_SM singlet, spin scalar, ghost number zero",
            1,
            "ALLOWED_CONDITIONALLY",
            "must not duplicate a retained bulk or intrinsic boundary term",
        ),
        InvariantDensity(
            "incidence_projector",
            "norms/traces of C(F_B)P_child-P_event C(F_B) and compatible discrete incidence tensors",
            "basis invariant and functorial under bundle transport",
            1,
            "ALLOWED_CONDITIONALLY",
            "physical projectors are not yet available, so this family is typed but unevaluable",
        ),
        InvariantDensity(
            "topological_holonomy",
            "quantized characteristic, holonomy, degree, or FR-compatible terms T_top",
            "gauge invariant modulo an allowed quantized phase",
            1,
            "OPTIONAL_DISCRETE_CLASS",
            "coefficient/level must be fixed by owned topology; no continuous fitted weight",
        ),
        InvariantDensity(
            "extrinsic_curvature_or_second_jet",
            "new K^2, shape curvature, or second F_B/embedding derivatives",
            "can be covariant",
            2,
            "NOT_REQUIRED",
            "excluded from the minimal class unless an independent higher-derivative extension is authorized",
        ),
        InvariantDensity(
            "owned_GHY_Hayward",
            "the already coefficient-locked GHY/corner completion on its declared geometric domain",
            "geometric scalar density",
            2,
            "REDUNDANT_NOT_NEW_INTERFACE_STRENGTH",
            "may contribute to total variation but cannot be counted again as P-A*",
        ),
    )
    return [asdict(row) for row in rows]


def derivative_order_adjudication() -> dict[str, Any]:
    return {
        "classification": DERIVATIVE_CLASS,
        "minimum": 1,
        "why_ORD0_fails": "connection and tensor transport under dynamical F_B requires D F_B",
        "why_ORD1_suffices_for_the_class": (
            "induced measure, conormal, first shape work, natural pullback, and sector canonical data "
            "can all be represented with first jets on regular pieces"
        ),
        "ORD2_not_required": (
            "extrinsic-curvature-square or second-map-jet terms would be a separate higher-derivative physical choice; "
            "owned GHY/Hayward terms remain in the old geometric action"
        ),
        "nonlocality": "topological/holonomy terms may be globally defined, but nonlocal constitutive dynamics is not forced",
    }


def invariant_control_arguments() -> dict[str, Any]:
    """Give the smallest currently typed invariant argument set."""

    scale = scale_and_control_ledger()
    energy = scale_and_energy_variables()
    return {
        "continuous_dimensionless": [
            "basis-invariant initiating-mode norm/action amplitude where owned",
            "event geometric scalar invariants on regular strata",
            "dimensionless contractions of B_s after a physical conormal/reference is available",
            "R_reset/ell_kappa",
            "x_s=log(B/A)|_(sigma=0)",
        ],
        "dimensionful_anchor": "ell_kappa=kappa1^(-1/6)",
        "discrete": ["alpha_s", "tau_s", "degree", "orientation", "FR parity", "incidence", "bundle/representation class"],
        "rho_E_over_ST": scale["rho_E/ST"],
        "available_energy_structures": energy["energy"],
        "excluded": [
            "rho_hold before common charges exist", "historical synthetic E_mode/E_impedance numbers",
            "Planck or phenomenological thresholds", "independent child-mode amplitudes",
        ],
        "result": "argument types are finite, but their universal constitutive dependence is not selected",
    }


def most_general_action_class() -> dict[str, Any]:
    """State the maximal local ORD1 action class without instantiating it."""

    return {
        "extended_action": "S_total=S_registered_13_terms+S_enc",
        "registered_action_relation": "P-A* is a new fourteenth authority class, not derived from or hidden in the prior terms",
        "schematic": (
            "S_enc=sum_s integral_(Sigma_enc^s) mu_gamma ell_kappa^(-n_s) "
            "W_s(I_mode,I_env,I_scale;q_e,C_s(F_B)q_c,Pi_e,C_s(F_B)^(-*)Pi_c,L_s,"
            "j1 F_B,j1 iota_enc)+T_top"
        ),
        "n_s": "dim Sigma_enc^s",
        "W_s": "real ghost-number-zero invariant scalar functions with no independently fitted interface parameters",
        "domain": "disjoint union of admissible regular carrier, map, Lagrangian-relation, field, environment, and superselection sectors",
        "codomain": "R modulo canonical exact boundary terms and any independently quantized topological phase",
        "equivalence": [
            "carrier total divergences with fixed corner data",
            "canonical exact generating-function changes that leave the relation invariant",
            "BRST-exact terms with zero physical reduced matrix element",
            "quantized topological phase equivalence where already owned",
        ],
        "density_selected": False,
        "zero_parameter_member_selected": False,
    }


def first_variation() -> dict[str, Any]:
    """Return the exact Euler-operator decomposition valid for every ORD1 member."""

    return {
        "variation": (
            "delta S_enc=sum_s[<E_Xe,delta X_e>+<E_Xc,delta X_c>+"
            "<E_iota,V>+<E_F,eta_c>+<E_L,ell_s>]+integral_(partial Sigma) theta_enc"
        ),
        "Euler_operator": "E_Y(W)=partial W/partial Y-nabla_a(partial W/partial(nabla_a Y))",
        "map_velocity": "eta_c=delta F_B o F_B^(-1)",
        "carrier_velocity": "V=delta iota_enc decomposed into tangential reparametrization plus physical normal deformation",
        "Lagrangian_variation": "ell_s in T_(L_s)Lag(T_s)",
        "corner_term": "theta_enc is fixed/cancelled by an owned corner ensemble; no new corner coefficient is selected",
        "well_posedness": "requires the chosen W_s Hessian/Legendre blocks and boundary ensemble to satisfy the relevant regularity conditions",
    }


def euler_lagrange_system() -> dict[str, Any]:
    """Give the total-action equations induced by a selected member."""

    return {
        "carrier": {
            "equation": "Pr_normal([T_bulk.n]_e,c+E_iota(S_enc))=0",
            "tangential_part": "Noether/reparametrization identity rather than an independent carrier equation",
            "selects_now": False,
        },
        "attachment": {
            "equation": (
                "for_all_admissible_eta: sum_s <Pi_e,s,D_F C_s(F_B)[eta] q_c,s>+D_F S_enc[eta]=0"
            ),
            "quotient": "modulo proven carrier reparametrization and internal gauge/spin lift redundancy",
            "selects_now": False,
        },
        "boundary_relation": {
            "equation": "Pr_(T_Ls Lag(T_s)) D_Ls S_enc=0 for every nonfermion sector s",
            "old_action_contribution": "zero/blind in the unselected family",
            "selects_now": False,
        },
        "event_field_seam": {
            "equation": "Pi_e+E_qe(S_enc)=0 on the reduced event trace bundle",
            "selects_now": False,
        },
        "child_field_seam": {
            "equation": "Pi_c+E_qc(S_enc)=0 on the reduced child trace bundle",
            "selects_now": False,
        },
        "constraint_projection": "all equations are projected to Hamiltonian, momentum, Gauss, BRST, incidence, FR, and retarded admissible directions",
        "reason_not_solved": "E(S_enc) is undefined until the constitutive functions W_s are selected",
    }


def active_encapsulation_differential() -> dict[str, Any]:
    """Derive Delta_enc from field variations in the existing sign convention."""

    return {
        "definition_from_total_seam_equations": (
            "Delta_enc:=Pi_c+C(F_B)^*Pi_e="
            "-[E_qc(S_enc)+C(F_B)^*E_qe(S_enc)]=:J_enc"
        ),
        "space": "constraint- and BRST-reduced child boundary cotangent bundle",
        "support": "support of the selected W_s on Sigma_enc and any declared environment seam variables",
        "amplitude": None,
        "mode_content": "only matched actual-stabilizer irreps after physical projectors exist",
        "sign": "fixed by opposite outward conormals and the displayed total-action convention",
        "covariance": "cotangent pullback under boundary diffeomorphisms and adjoint covariance on reduced gauge blocks",
        "scale": "ell_kappa dimensional weight times unselected dimensionless response functions",
        "critical_passive_no_go": (
            "if S_enc depends only on q_e-C(F_B)q_c, then E_qc+C^*E_qe=0 and Delta_enc=0; "
            "such a mismatch penalty cannot represent active creation/erasure/redistribution"
        ),
        "value_derived": False,
    }


def no_ex_nihilo_noether_structure() -> dict[str, Any]:
    """Encode conservation as Ward identities rather than a guessed scalar energy law."""

    old = constraint_noether_ledger()
    return {
        "principle": "diagonal symmetry of S_total produces the interface Ward/Noether balance",
        "local_identity": "d J_total_xi=0 in the closed extended event+child+interface/environment system",
        "seam_identity": "J_event+J_child+J_interface+J_environment=0 with orientations fixed by the two conormals",
        "canonical_identity": "Delta_enc=J_enc=-Pi_interface_environment in the displayed convention",
        "integrated_energy_form": (
            "H_xi(e)=H_xi(c)+H_xi(interface/environment)+sum_i H_xi(c_i)+Phi_out "
            "only after xi, reference, ensemble, and common domain exist"
        ),
        "fixed_control_caveat": (
            "if E_s is held external, its variation appears as an explicit work/source term; "
            "it may not be hidden as child energy or called closed-system conservation"
        ),
        "information_balance": (
            "noninvertible boundary-information reduction is allowed only with the complementary "
            "interface/environment degrees recorded in J_enc"
        ),
        "existing_response_conditions": old["remaining_response_conditions"],
        "numerical_charge_balance_evaluable": False,
    }


def canonical_lagrangian_status() -> dict[str, Any]:
    old = canonical_structure_ledger()
    return {
        "generated_relation": (
            "Crit_(iota,F,L,aux) S_enc defines an exact isotropic correspondence in "
            "P_event^- x P_child when the reduced symplectic form and regular generating-family hypotheses hold"
        ),
        "isotropy_condition": old["response_pullback"],
        "Lagrangian_condition": old["Lagrangian_condition"],
        "constraint_reduction": "perform coisotropic Hamiltonian/momentum/Gauss/BRST reduction before maximality",
        "conditional_status": "CANONICAL_GENERATING_FAMILY_CLASS_DERIVED",
        "actual_isotropy_verified": False,
        "actual_Lagrangian_verified": False,
        "why": "no W_s, physical carrier, complete reduced symplectic domain, or Hessian/transversality data are selected",
    }


def classify_density_candidate(candidate: DensityCandidate) -> dict[str, Any]:
    """Fail closed on convenient but unauthorized interface densities."""

    failures: list[str] = []
    if candidate.derivative_order > 1:
        failures.append("HIGHER_DERIVATIVE_EXTENSION_NOT_REQUIRED_OR_AUTHORIZED")
    for flag, message in (
        (candidate.scalar_density, "NOT_A_CARRIER_SCALAR_DENSITY"),
        (candidate.gauge_invariant, "GAUGE_NONINVARIANT"),
        (candidate.brst_compatible, "BRST_INCOMPATIBLE"),
        (candidate.spin_covariant, "SPIN_NONCOVARIANT"),
        (candidate.orientation_fr_compatible, "ORIENTATION_OR_FR_INCOMPATIBLE"),
        (candidate.event_mode_conditioned, "NOT_EVENT_MODE_CONDITIONED"),
        (candidate.environment_scale_conditioned, "NOT_ENVIRONMENT_AND_SCALE_CONDITIONED"),
    ):
        if not flag:
            failures.append(message)
    if candidate.independent_fitted_parameters:
        failures.append("INDEPENDENT_FITTED_INTERFACE_PARAMETERS_FORBIDDEN")
    if candidate.child_coefficients_as_controls:
        failures.append("INDEPENDENT_CHILD_MODE_COEFFICIENTS_FORBIDDEN")
    if candidate.passive_mismatch_only:
        failures.append("PASSIVE_MISMATCH_ONLY_GIVES_ZERO_ACTIVE_DIFFERENTIAL")
    if candidate.duplicates_owned_ghy_or_bulk_term:
        failures.append("DUPLICATES_OWNED_ACTION_TERM")
    return {
        "name": candidate.name,
        "admissible_class_member": not failures,
        "failures": failures,
        "physical_member_selected": False,
    }


def adversarial_density_ledger() -> list[dict[str, Any]]:
    candidates = (
        DensityCandidate("constant_surface_tension", 0, True, True, True, True, True, False, False, True),
        DensityCandidate("passive_trace_mismatch_penalty", 0, True, True, True, True, True, True, True, passive_mismatch_only=True),
        DensityCandidate("fitted_event_threshold", 0, True, True, True, True, True, True, True, independent_fitted_parameters=True),
        DensityCandidate("child_harmonic_coefficients", 0, True, True, True, True, True, True, True, child_coefficients_as_controls=True),
        DensityCandidate("bare_gauge_potential_norm", 0, True, False, False, True, True, True, True),
        DensityCandidate("new_extrinsic_curvature_square", 2, True, True, True, True, True, True, True),
        DensityCandidate("duplicate_GHY", 1, True, True, True, True, True, True, True, duplicates_owned_ghy_or_bulk_term=True),
    )
    return [classify_density_candidate(candidate) for candidate in candidates]


def active_differential_from_gradients(
    event_gradient: Sequence[float],
    child_gradient: Sequence[float],
    child_to_event: Sequence[Sequence[float]],
) -> np.ndarray:
    """Return ``-[D_qc S + C^T D_qe S]`` in a finite real chart."""

    ge = np.asarray(event_gradient, dtype=float)
    gc = np.asarray(child_gradient, dtype=float)
    transport = np.asarray(child_to_event, dtype=float)
    if ge.ndim != 1 or gc.ndim != 1 or transport.shape != (ge.size, gc.size):
        raise ValueError("incompatible event/child cotangent dimensions")
    return -(gc + transport.T @ ge)


def passive_mismatch_active_differential(
    event_trace: Sequence[float],
    child_trace: Sequence[float],
    child_to_event: Sequence[Sequence[float]],
) -> np.ndarray:
    """Show that a quadratic mismatch action gives no active differential."""

    qe = np.asarray(event_trace, dtype=float)
    qc = np.asarray(child_trace, dtype=float)
    transport = np.asarray(child_to_event, dtype=float)
    if transport.shape != (qe.size, qc.size):
        raise ValueError("incompatible event/child trace dimensions")
    residual = qe - transport @ qc
    grad_event = residual
    grad_child = -transport.T @ residual
    return active_differential_from_gradients(grad_event, grad_child, transport)


def pullback_isotropy_residual(
    trace_jacobian: Sequence[Sequence[float]],
    momentum_jacobian: Sequence[Sequence[float]],
) -> float:
    """Measure ``||(Dq)^T DPi-(DPi)^T Dq||`` in a finite chart."""

    dq = np.asarray(trace_jacobian, dtype=float)
    dpi = np.asarray(momentum_jacobian, dtype=float)
    if dq.ndim != 2 or dpi.shape != dq.shape:
        raise ValueError("trace and momentum Jacobians must have equal matrix shape")
    return float(np.linalg.norm(dq.T @ dpi - dpi.T @ dq))


def parameter_freedom_adjudication() -> dict[str, Any]:
    return {
        "classification": INTERFACE_FREEDOM_CLASS,
        "owner_authorization_removes": [
            "independent phenomenological interface coefficients",
            "child amplitudes independent of the initiating event",
            "mode-blind or environment-blind interface laws",
        ],
        "remaining": [
            "unselected universal scalar functions of event/environment/scale invariants",
            "matrix-valued functions on matched irreps with multiplicity",
            "potentially operator-valued kernels on full boundary section spaces",
            "choice of active interface/environment degrees carrying missing information and Noether work",
            "discrete topological/holonomy classes whose level is not already fixed",
        ],
        "why_not_IF0_or_IF1": "covariance and dimensions permit more than one inequivalent invariant function even with ell_kappa normalization",
        "why_not_IF2_or_IF3": "the allowed dependence is functional, not a finite list of discrete branches or constants",
        "why_not_IF4": "unresolved multiplicities, carrier/base-map freedom, and section-space kernels prevent a finite function count",
        "functions_selected": 0,
        "coefficients_fitted": 0,
    }


def historical_candidate_comparison() -> list[dict[str, Any]]:
    return [
        {"candidate": "v6.10 junction action", "within_allowed_class": "ZERO_OR_OPTIONAL_MEMBER_ONLY", "selected": False, "reason": "old action has no junction mixing term and selects no graph"},
        {"candidate": "v14.60-v14.61 global envelopment", "within_allowed_class": "FINITE_SYNTHETIC_TRUNCATION", "selected": False, "reason": "witness coefficients and operators are nonphysical and branch/domain data are open"},
        {"candidate": "historical boundary-action branches", "within_allowed_class": "STRUCTURAL_SUBCLASS", "selected": False, "reason": "coframe/winding/primitive quotient and normalization are unproved"},
        {"candidate": "v15 master and Unique Actualization", "within_allowed_class": "OWNER_SEMANTICS", "selected": False, "reason": "no emergence or reconstruction functor supplies W_s"},
        {"candidate": "AE4 impedance/core crossing", "within_allowed_class": "POSSIBLE_INVARIANT_ARGUMENT", "selected": False, "reason": "charges, carrier, reference, and physical crossing function remain undefined"},
        {"candidate": "Calderon/DtN/Wentzell", "within_allowed_class": "CONDITIONAL_RESPONSE_OPERATOR_BLOCK", "selected": False, "reason": "requires the physical carrier/domain and does not determine the constitutive source"},
    ]


def closure_and_rank_status() -> dict[str, Any]:
    return {
        "selected_carrier": None,
        "selected_F_B": None,
        "selected_L_s": None,
        "physical_reset_domain": None,
        "moving_domain_tangent_verdict": "NOT_REACHED_NO_SELECTED_MEMBER_OF_IF5_CLASS",
        "loop": LOOP_CLASS,
        "charge_classes": "XI5_CHG4_REF5_MODEE5_ENVH5_DOMH4_AE4R5_UNCHANGED",
        "rho_hold": None,
        "N12_rank_ledger": [
            {"variation": "delta iota_enc", "raw_equations": None, "independent_rank": 0, "reason": "Euler operator uninstantiated"},
            {"variation": "delta F_B", "raw_equations": None, "independent_rank": 0, "reason": "Euler operator uninstantiated"},
            {"variation": "delta L_s", "raw_equations": None, "independent_rank": 0, "reason": "Euler operator uninstantiated"},
            {"variation": "delta X_e,delta X_c", "raw_equations": None, "independent_rank": 0, "reason": "seam source uninstantiated"},
        ],
        "N12_rank_added": 0,
        "N12_residual_before_time_quotient": 67,
        "N12_residual_after_time_quotient": 66,
        "unique_actualization": UNIQUE_ACTUALIZATION_CLASS,
        "actualization_set": "union over the unselected IF5 functional class, carriers, maps, relations, and BVP solutions",
        "S1": None,
        "S2": None,
        "S3": None,
        "S4": None,
        "full_field_attachment": None,
    }


def claim_boundary() -> dict[str, bool]:
    return {
        "OWNER_AUTHORIZED_PRIMITIVE_RECORDED": True,
        "PRIMITIVE_DERIVED_FROM_OLD_ACTION": False,
        "CONSTITUTIVE_DENSITY_SELECTED": False,
        "PHYSICAL_CARRIER_SELECTED": False,
        "PHYSICAL_RESET_SELECTED": False,
        "DELTA_ENC_VALUE_DERIVED": False,
        "COMMON_CHARGE_DERIVED": False,
        "NEW_N12_RANK_COUNTED": False,
        "FROZEN_PREDICTIONS_CHANGED": False,
        "GATE7_PROMOTED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def interface_action_payload() -> dict[str, Any]:
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "authority": owner_authorization(),
        "variables": interface_variable_contract(),
        "controls": control_state_contract(),
        "symmetry": symmetry_contract(),
        "invariant_densities": invariant_density_ledger(),
        "derivative_order": derivative_order_adjudication(),
        "invariant_controls": invariant_control_arguments(),
        "action_class": most_general_action_class(),
        "first_variation": first_variation(),
        "Euler_Lagrange_system": euler_lagrange_system(),
        "active_differential": active_encapsulation_differential(),
        "no_ex_nihilo": no_ex_nihilo_noether_structure(),
        "canonical_Lagrangian": canonical_lagrangian_status(),
        "parameter_freedom": parameter_freedom_adjudication(),
        "historical_candidates": historical_candidate_comparison(),
        "adversarial_candidates": adversarial_density_ledger(),
        "closure_and_rank": closure_and_rank_status(),
        "exact_next_object": EXACT_NEXT_OBJECT,
        "owner_question": None,
        "why_no_owner_question": "IF5 is not a small finite ambiguity; asking for an arbitrary function would violate the directive",
        "claim_boundary": claim_boundary(),
        "prior_contracts_reused": {
            "output_space": output_space_contract(),
            "scale_controls": scale_and_control_ledger(),
        },
    }


__all__ = [
    "ACTION_VERSION", "CLASSIFICATION", "DERIVATIVE_CLASS", "DensityCandidate",
    "EXACT_NEXT_OBJECT", "INTERFACE_FREEDOM_CLASS", "LOOP_CLASS",
    "UNIQUE_ACTUALIZATION_CLASS", "active_differential_from_gradients",
    "active_encapsulation_differential", "adversarial_density_ledger",
    "canonical_lagrangian_status", "claim_boundary", "classify_density_candidate",
    "closure_and_rank_status", "control_state_contract", "derivative_order_adjudication",
    "euler_lagrange_system", "first_variation", "historical_candidate_comparison",
    "interface_action_payload", "interface_variable_contract", "invariant_control_arguments",
    "invariant_density_ledger", "most_general_action_class", "no_ex_nihilo_noether_structure",
    "owner_authorization", "parameter_freedom_adjudication",
    "passive_mismatch_active_differential", "pullback_isotropy_residual", "symmetry_contract",
]
