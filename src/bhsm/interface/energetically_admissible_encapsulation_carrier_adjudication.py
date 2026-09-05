"""Adjudicate action-owned energetic support for an encapsulation carrier.

This module composes the recovered BHSM energy, support, scale, enclosure,
and event/child lineages.  It deliberately separates the already selected
AE3 ``sigma=0`` *local material carrier* from the still-unselected physical
event-to-child encapsulation carrier.  No response function is fitted here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Iterable, Sequence


ACTION_VERSION = "BHSM-AE-3.2.12-ENERGETIC-CARRIER-ADJUDICATION"
CLASSIFICATION = "ENERGETICALLY_ADMISSIBLE_ENCAPSULATION_CARRIER_ADJUDICATION"


@dataclass(frozen=True)
class EnergyGeometryCandidate:
    """One recovered energy--geometry or envelopment candidate."""

    candidate_id: str
    energy_quantity: str
    geometry_quantity: str
    locality: str
    covariance: str
    relevant_stratum_domain: str
    units: str
    scale_dependence: str
    historical_envelopment_role: str
    current_status: str


def recovered_energy_geometry_candidates() -> list[dict[str, str]]:
    """Return the fail-closed lineage audit requested by the owner rule."""

    rows: Iterable[EnergyGeometryCandidate] = (
        EnergyGeometryCandidate(
            "V6_0_5_ENERGY_GEOMETRY_DIFFERENTIAL",
            "qualitative energy differential; no closed Hamiltonian charge",
            "local geometry variation",
            "local/formal",
            "covariant only after the missing action and boundary data",
            "regular stratum only",
            "not fixed as an energy functional",
            "qualitative",
            "historical doctrine for energy--geometry response",
            "RECOVERED_PRECURSOR_NOT_AN_ENVELOPMENT_COST",
        ),
        EnergyGeometryCandidate(
            "T_CORE_MATCHING",
            "postulated core matching energy",
            "multiplicative-support/core endpoint",
            "endpoint/global",
            "scalar support variable is covariant on the regular domain",
            "ordinary energy is undefined on C_A",
            "energy only after an unfixed normalization",
            "q_D=-lambda_D log(upsilon); endpoint is infinite depth",
            "candidate threshold and exit condition",
            "OPEN_NO_ACTION_OWNED_MATCHING_ENERGY",
        ),
        EnergyGeometryCandidate(
            "LOCAL_NOETHER_STRESS_IDENTITY",
            "total stress tensor and Noether current/flux",
            "spacetime hypersurface and boundary flux",
            "local differential identity",
            "covariant on shell with all field and connection equations",
            "regular bulk and typed boundaries",
            "stress density / current; integrated charge after a time flow",
            "depends on the selected flow and surface",
            "conservation firewall",
            "VALIDATED_PRIMARY_CONSERVATION_FORM_NOT_A_POSITIVE_SCALAR_BUDGET",
        ),
        EnergyGeometryCandidate(
            "BROWN_YORK_QUASILOCAL_ENERGY",
            "boundary-improved quasilocal Hamiltonian charge",
            "embedded codimension-one/two boundary geometry",
            "quasilocal",
            "covariant after normal, time flow, reference, and ensemble are fixed",
            "only on a selected regular carrier with corner data",
            "energy",
            "surface size, curvature, reference, and environment dependent",
            "strongest candidate for available/cost accounting",
            "OPEN_UNTIL_CARRIER_TIME_FLOW_REFERENCE_AND_ENSEMBLE_ARE_SELECTED",
        ),
        EnergyGeometryCandidate(
            "CLOSED_S7_HAMILTONIAN_CONSTRAINT",
            "constraint-reduced canonical Hamiltonian",
            "closed S7 slice",
            "global/canonical",
            "generally covariant constraint",
            "closed regular slice",
            "energy constraint",
            "no positive scale budget",
            "possible total-energy source",
            "INVALIDATED_AS_POSITIVE_AVAILABLE_ENERGY_BECAUSE_THE_CONSTRAINT_VANISHES",
        ),
        EnergyGeometryCandidate(
            "N12_LEGENDRE_ENERGY",
            "E_N=partial_v L dot v-L",
            "N12 event and child trajectory",
            "finite Galerkin/canonical",
            "coordinate-canonical within N12",
            "N12 constrained branch only",
            "energy",
            "inherits N12 nondimensionalization",
            "constraint-compatible Galerkin energy candidate",
            "INVALIDATED_AS_AVAILABLE_ENERGY_ON_THE_CONSTRAINT_SET_E_N_EQUALS_ZERO",
        ),
        EnergyGeometryCandidate(
            "AE3_FAMILY_HARMONIC_ENERGY",
            "mode displacement/spectral stiffness candidate",
            "family-harmonic localization geometry",
            "local reduced sector",
            "covariant only within the frozen reduced construction",
            "AE3 family fiber",
            "energy after action normalization",
            "mode and localization scale dependent",
            "initiating-mode energy candidate",
            "OPEN_PARENT_ACTION_MODE_ENERGY_NOT_EVALUATED",
        ),
        EnergyGeometryCandidate(
            "SUPPORT_HAAR_DEPTH",
            "bare q_D potential is zero in the canonical crystallization audit",
            "q_D=-lambda_D log(upsilon)",
            "local on the regular support stratum",
            "diffeomorphism scalar after constraint reduction",
            "0<upsilon<=1; C_A is a separate stratum",
            "dimensionless depth; energy normalization absent",
            "logarithmic and divergent at support loss",
            "enclosure-depth candidate",
            "VALIDATED_AS_DEPTH_COORDINATE_NOT_AS_ENVELOPMENT_ENERGY",
        ),
        EnergyGeometryCandidate(
            "ENERGY_GEOMETRY_CONFINEMENT_INVARIANTS",
            "stress/flux/interface/quasilocal candidates",
            "curvature, Lovelock, trace, K, K2, pressure, coherence",
            "mixed local/interface/quasilocal",
            "each candidate has its own covariance and measure requirements",
            "regular typed domains only",
            "heterogeneous; cannot be quotient-combined without measures",
            "curvature and spectral scales",
            "finite conditional diagnostic list",
            "RHO_CANDIDATES_NOT_COSELECTED_BY_THE_ACTION",
        ),
        EnergyGeometryCandidate(
            "GLOBAL_ENVELOPMENT_REDUCED_FUNCTIONAL",
            "synthetic reduced objective, not a physical charge",
            "interior/seam/scale fixture",
            "global reduced fixture",
            "conditional on the chosen reduction",
            "fixture domain",
            "synthetic objective units",
            "explicit fixture scale variables",
            "tests joint stationarity architecture",
            "VALIDATED_CONDITIONAL_FIXTURE_NOT_PROMOTED_TO_E_ENVLP",
        ),
        EnergyGeometryCandidate(
            "AE4_IMPEDANCE_CORE_CROSSING",
            "E_impedance[Phi;Sigma] and E_core[Phi;Sigma] (unevaluated)",
            "first future surface where equality holds and outward support ceases",
            "surface/quasilocal proposal",
            "intended covariant surface rule; full operator/domain missing",
            "not evaluable on current C2",
            "energy; ell_star=1/E_impedance in natural units",
            "defines a conditional carrier scale",
            "strongest recovered physical carrier-selection architecture",
            "OPEN_HYPOTHESIS_NOT_AN_INSTANTIATED_CARRIER",
        ),
        EnergyGeometryCandidate(
            "KKT_TANGENT_RESPONSE",
            "first-order response multiplier, not an energy budget",
            "constraint tangent geometry",
            "local reduced system",
            "covariant only inside its fixed reduction",
            "KKT fixture domain",
            "dual-to-constraint units",
            "depends on fixed normalization",
            "response diagnostic",
            "REDUNDANT_FOR_ENERGETIC_CARRIER_SELECTION",
        ),
    )
    return [asdict(row) for row in rows]


def available_event_energy_status() -> dict[str, object]:
    """State the strongest earned type for ``E_avail`` without inventing it."""

    return {
        "symbol": "E_avail[M_event;E_s,Lambda_s]",
        "defined": False,
        "classification": "OPEN_TYPED_CHARGE_DIFFERENCE",
        "strongest_admissible_definition": (
            "boundary-improved covariant Hamiltonian/Noether charge for a selected "
            "time flow xi and carrier, projected to the initiating mode, minus the "
            "charge constrained to remain in other degrees of freedom"
        ),
        "E_avail_equals_E_mode": "NOT_DERIVED",
        "total_environmental_energy_equals_E_avail": False,
        "missing_map": (
            "(full_action,solution,xi,carrier,reference,ensemble,mode_projector)"
            " -> integrable charge decomposition"
        ),
    }


def envelopment_requirement_status() -> dict[str, object]:
    """State the strongest admissible type for ``E_envlp``."""

    return {
        "symbol": "E_envlp[Sigma;E_s,Lambda_s]",
        "defined": False,
        "classification": "OPEN_BOUNDARY_IMPROVED_ON_SHELL_COST",
        "strongest_admissible_definition": (
            "on-shell boundary-improved Hamiltonian/quasilocal charge increment "
            "for the proposed child plus seam geometry relative to a compatible "
            "reference, including gravitational boundary/corner, matter, and "
            "constraint contributions"
        ),
        "universal_price_per_volume": False,
        "global_envelopment_fixture_is_E_envlp": False,
        "missing_map": (
            "(Sigma,child_solution,seam_data,xi,reference,ensemble)"
            " -> integrable quasilocal charge increment"
        ),
    }


def _nonnegative_finite(name: str, value: float) -> float:
    numeric = float(value)
    if not isfinite(numeric) or numeric < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return numeric


def energetic_feasibility(
    available: float, required: float, *, compensating_source: float = 0.0
) -> bool:
    """Evaluate the owner inequality after, and only after, charges are supplied.

    This diagnostic does not define any of its arguments and is not a carrier
    selector.  A compensating source must be an independently action-owned
    contribution in any physical use.
    """

    lhs = _nonnegative_finite("available", available)
    rhs = _nonnegative_finite("required", required)
    source = _nonnegative_finite("compensating_source", compensating_source)
    return rhs <= lhs + source


def oriented_energy_balance_residual(
    event_input: float,
    primary_child: float,
    seam_environment: float,
    *,
    additional_children: Sequence[float] = (),
    outward_flux: float = 0.0,
) -> float:
    """Return the scalar balance residual for already-integrable charges."""

    event = _nonnegative_finite("event_input", event_input)
    child = _nonnegative_finite("primary_child", primary_child)
    seam = _nonnegative_finite("seam_environment", seam_environment)
    flux = _nonnegative_finite("outward_flux", outward_flux)
    other = sum(
        _nonnegative_finite(f"additional_children[{index}]", value)
        for index, value in enumerate(additional_children)
    )
    return event - child - seam - other - flux


def conservation_firewall() -> dict[str, object]:
    """Return the covariant primary law and its conditional scalar reduction."""

    return {
        "primary_form": (
            "nabla_A T_total^{AB}=sum_fields E_field nabla^B(field) + "
            "connection_equations + boundary_flux"
        ),
        "boundary_charge_form": (
            "Q_xi[Sigma_2]-Q_xi[Sigma_1] = - integral_timelike_boundary J_xi"
        ),
        "conditional_integrable_scalar_form": (
            "H_xi(event)=H_xi(primary_child)+H_xi(seam/environment)+"
            "sum_i H_xi(additional_child_i)+outward_flux"
        ),
        "scalar_form_conditions": [
            "selected time flow xi",
            "integrable boundary-improved charges",
            "compatible reference and ensemble",
            "oriented carrier and corner data",
        ],
        "closed_generally_covariant_Hamiltonian_is_positive_total_energy": False,
        "reset_may_supply_missing_energy": False,
        "independent_energy_bearing_actualization": "SEPARATE_CHILD_CANDIDATE",
    }


def rho_status() -> dict[str, object]:
    """Classify the owner energy/spacetime control variable."""

    return {
        "classification": "RHO5",
        "privileged_scalar_derived": False,
        "reason": (
            "Neither E_avail nor E_envlp is an instantiated invariant charge; "
            "time flow, reference, ensemble, mode projection, carrier, and domain "
            "choices remain unselected.  Ordinary energy is undefined on C_A."
        ),
        "closest_recovered_hypothesis": {
            "symbol": "rho_hold=E_mode/E_impedance[Phi;Sigma_enclosure]",
            "weak_or_stable": "rho_hold<1 (hypothesized)",
            "crossing": "rho_hold=1 (hypothesized)",
            "promotion": "NOT_EVALUATED_OR_ACTION_DERIVED",
        },
        "regime_audit": {
            "weak_envelopment": "UNEVALUABLE_WITHOUT_CHARGES",
            "regular_spacetime": "CANDIDATE_FUNCTIONALS_EXIST_BUT_NONE_IS_PRIVILEGED",
            "strong_envelopment": "UNEVALUABLE_WITHOUT_A_SELECTED_BRANCH",
            "spacetime_edge": "ONLY_LAST_REGULAR_TRACE_COULD_CARRY_AN_ORDINARY_CHARGE",
            "C_A": "ORDINARY_ENERGY_NOT_EVALUATED_ON_THE_SINGULAR_STRATUM",
        },
    }


def scale_status() -> dict[str, object]:
    """Return owned scale coordinates and non-arbitrary trigger candidates."""

    return {
        "descriptor": "Lambda_s=(ell_kappa,R_reset/ell_kappa,x_s,...owned dimensionless environmental data)",
        "ell_kappa": "kappa_1^(-1/6)",
        "R_star_relation": "R_star=2.0232708255441265 ell_kappa",
        "R_star_role": "environmental reset reconstruction relation, not an envelopment price law",
        "manual_Planck_threshold_inserted": False,
        "candidate_triggers": [
            {
                "trigger": "E_impedance=E_core with outward support cessation",
                "status": "AE4_OWNER_RULE_UNEVALUATED",
            },
            {"trigger": "lambda_phys=0", "status": "CONDITIONAL_OPERATOR_DOMAIN_OPEN"},
            {"trigger": "lambda_surface=0", "status": "DEFINED_BUT_NO_ROOT_DERIVED"},
            {"trigger": "Jensen tachyon crossing", "status": "INVALIDATED_NO_CROSSING_AT_FINITE_TIME"},
            {"trigger": "new decay/channel threshold", "status": "OPEN_MASSES_AND_AMPLITUDES_NOT_ACTION_DERIVED"},
        ],
    }


def admissible_carrier_family() -> dict[str, object]:
    """Describe the carrier family without pretending its predicates evaluate."""

    return {
        "symbol": "S_enc",
        "formal_type": (
            "{Sigma in typed regular surfaces/cuts/seams/last-regular traces/"
            "reconstruction boundaries: event compatibility AND environmental "
            "support AND full-field domain admissibility AND energetic feasibility}"
        ),
        "set_evaluable_now": False,
        "local_AE3_subsystem_carrier": {
            "surface": "Sigma_enc={sigma=0}",
            "inside": "D_enc={sigma<0}",
            "classification": "CARR1_WITHIN_THE_ETA_SIGMA_LOCALIZATION_SUBSYSTEM",
            "geometry": "unique regular identity-branch level set at chi=pi/4",
            "physical_scope": "resolved internal material level set",
            "terminal_reset_boundary": False,
            "energy_selected": False,
        },
        "full_event_to_child_carrier": {
            "classification": "CARR5",
            "reason": (
                "the energetic predicates and full-field boundary domains cannot be "
                "evaluated, leaving an infinite-dimensional surface freedom"
            ),
        },
        "strongest_selection_architecture": (
            "FIRST_FUTURE_SURFACE_WHERE_E_impedance[Phi;Sigma]=E_core[Phi;Sigma] "
            "AND_OUTWARD_SPACETIME_SUPPORT_CEASES"
        ),
    }


def carrier_selection_verdict() -> dict[str, object]:
    return {
        "full_classification": "CARR5",
        "saturation_derived": False,
        "first_positive_return_selects_geometry": False,
        "first_positive_return_role": "set-valued event-to-child timing/reconstruction relation",
        "physical_stationarity_derived": False,
        "constraint_closure_selects_carrier": False,
        "global_envelopment_extremality": "CONDITIONAL_SYNTHETIC_FIXTURE_ONLY",
        "exact_blocking_map": (
            "(full_action, event solution, environment, Lambda_s, candidate Sigma) "
            "-> (integrable E_avail, integrable E_envlp, admissible full-field domain)"
        ),
    }


def multiple_child_status() -> dict[str, object]:
    return {
        "generic_readout_machinery": "1->2, 1->3, and 1->n phase-space/channel combinatorics recovered",
        "action_owned_branching_dynamics": False,
        "missing": ["physical masses", "vertices/amplitudes", "complete channel ledger", "multi-child incidence"],
        "one_child_with_internal_modes_is_multiple_children": False,
        "owner_rule_effect": (
            "an independently actualized energy-bearing branch must be ledgered as "
            "a distinct child, but the rule alone creates no branch"
        ),
    }


def boundary_operator_package() -> dict[str, object]:
    """Delimit what can and cannot be instantiated at CARR5."""

    sectors = ["geometry", "scalar/topographic", "gauge", "fermion", "ghost", "higher_spin"]
    return {
        "event_boundary_space": "OPEN_FULL_FIELD_TRACE_AND_CONORMAL_SPACE",
        "child_boundary_space": "OPEN_FULL_FIELD_TRACE_AND_CONORMAL_SPACE",
        "event_operator_domains": "OPEN_BEYOND_CONDITIONAL_OR_FINITE_GALERKIN_DOMAINS",
        "child_operator_domains": "OPEN_BEYOND_CONDITIONAL_OR_FINITE_GALERKIN_DOMAINS",
        "required_sectors": sectors,
        "AE3_local_partial_package": {
            "carrier": "sigma=0",
            "available_traces": "geometry plus eta/sigma regular traces with smooth same-action matching",
            "terminal_boundary_condition": False,
            "six_sector_closure": False,
        },
        "physical_Calderon_or_DtN_operators": "NOT_INSTANTIATED",
    }


def stabilizer_spectral_incidence_status() -> dict[str, object]:
    return {
        "actual_stabilizer": "OPEN_INTERSECTION_Stab(z_event,E_s,M_event,Sigma_enc)",
        "default_full_Diff_or_Spin4_or_SU2_used": False,
        "physical_isotypic_decomposition": "OPEN_UNTIL_G_x_AND_BOUNDARY_HILBERT_SPACES_EXIST",
        "spectral_projectors": "OPEN",
        "event_to_child_incidence": "OPEN_AT_FULL_PHYSICAL_LEVEL",
        "AE3_local_transport": (
            "frozen family-mode tensor-factor transport and projector commutation "
            "are algebraically derived on sigma=0"
        ),
        "initiating_mode_inheritance": (
            "family/representation/topological labels transport conditionally; "
            "amplitude, phase, and energy allocation do not follow automatically"
        ),
    }


def response_and_active_differential_status() -> dict[str, object]:
    return {
        "response_classification": "RSP5",
        "why": (
            "the full carrier, boundary spaces, domains, stabilizer, projectors, "
            "and physical incidence remain uninstantiated"
        ),
        "active_differential": "Delta_enc=Pi_child+C(F_B)^*Pi_event",
        "support": "CONDITIONAL_LOCAL_SIGMA_ZERO_SUPPORT_FOR_ATTACHED_AE3_SUBSYSTEM_ONLY",
        "mode_content": "OPEN_AT_FULL_FIELD_LEVEL",
        "amplitude": "OPEN",
        "sign": "OPEN",
        "geometric_location": "OPEN_FOR_FULL_EVENT_TO_CHILD_CARRIER",
        "F_B_selected": False,
    }


def n12_rank_ledger() -> dict[str, object]:
    rows = [
        {"source": "owner energetic semantics", "raw_equations": 0, "independent_rank": 0, "residual": 67},
        {"source": "representation decomposition", "raw_equations": 0, "independent_rank": 0, "residual": 67},
        {"source": "AE3 local sigma carrier (already owned, not a new N12 equation)", "raw_equations": 0, "independent_rank": 0, "residual": 67},
        {"source": "current energetic-carrier adjudication", "raw_equations": 0, "independent_rank": 0, "residual": 67},
    ]
    return {
        "baseline": "98-31=67",
        "rows": rows,
        "actual_new_rank": 0,
        "residual_before_time_quotient": 67,
        "residual_after_time_quotient": 66,
    }


def claim_boundary() -> dict[str, bool]:
    return {
        "AE3_SIGMA_ZERO_LOCAL_MATERIAL_CARRIER_ACTION_OWNED": True,
        "AE3_SIGMA_ZERO_IS_TERMINAL_RESET_BOUNDARY": False,
        "FULL_EVENT_TO_CHILD_ENCAPSULATION_CARRIER_SELECTED": False,
        "E_AVAIL_ACTION_OWNED_AND_EVALUABLE": False,
        "E_ENVLP_ACTION_OWNED_AND_EVALUABLE": False,
        "NO_EX_NIHILO_CONSERVATION_FIREWALL_FORMALIZED": True,
        "RHO_E_ST_PRIVILEGED_SCALAR_DERIVED": False,
        "PLANCK_THRESHOLD_INSERTED": False,
        "MULTIPLE_CHILD_DYNAMICS_DERIVED": False,
        "FULL_BOUNDARY_OPERATOR_PACKAGE_INSTANTIATED": False,
        "ACTUAL_STABILIZER_DERIVED": False,
        "PHYSICAL_SPECTRAL_PROJECTORS_DERIVED": False,
        "FULL_EVENT_TO_CHILD_INCIDENCE_DERIVED": False,
        "ENCAPSULATION_RESPONSE_FUNCTION_SELECTED": False,
        "FROZEN_PREDICTIONS_MODIFIED": False,
        "GATE7_PROMOTED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def exact_next_object() -> dict[str, str]:
    return {
        "object": "BOUNDARY_IMPROVED_EVENT_MODE_AND_ENVELOPMENT_CHARGE_MAP",
        "map": (
            "(full_action,event_solution,environment,Lambda_s,Sigma,xi,reference,ensemble,"
            "mode_projector)->(H_xi_mode_available,Delta_H_xi_child_plus_seam)"
        ),
        "acceptance": (
            "integrability, common reference/ensemble, full-field domains, conserved "
            "oriented balance, and evaluability on every surviving regular carrier"
        ),
    }


def adjudication_payload() -> dict[str, object]:
    """Return the deterministic source-level adjudication payload."""

    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "recovered_candidates": recovered_energy_geometry_candidates(),
        "available_event_energy": available_event_energy_status(),
        "envelopment_requirement": envelopment_requirement_status(),
        "conservation": conservation_firewall(),
        "rho": rho_status(),
        "scale": scale_status(),
        "carrier_family": admissible_carrier_family(),
        "carrier_selection": carrier_selection_verdict(),
        "multiple_children": multiple_child_status(),
        "boundary_operator_package": boundary_operator_package(),
        "stabilizer_spectral_incidence": stabilizer_spectral_incidence_status(),
        "response_and_active_differential": response_and_active_differential_status(),
        "n12_rank": n12_rank_ledger(),
        "claim_boundary": claim_boundary(),
        "exact_next_object": exact_next_object(),
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "adjudication_payload",
    "admissible_carrier_family",
    "available_event_energy_status",
    "boundary_operator_package",
    "carrier_selection_verdict",
    "claim_boundary",
    "conservation_firewall",
    "energetic_feasibility",
    "envelopment_requirement_status",
    "exact_next_object",
    "multiple_child_status",
    "n12_rank_ledger",
    "oriented_energy_balance_residual",
    "recovered_energy_geometry_candidates",
    "response_and_active_differential_status",
    "rho_status",
    "scale_status",
    "stabilizer_spectral_incidence_status",
]
