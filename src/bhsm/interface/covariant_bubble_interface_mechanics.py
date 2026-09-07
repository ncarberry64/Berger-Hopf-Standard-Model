"""Minimal covariant BHSM bubble/interface mechanics on regular strata.

The owner-supplied bubble-mechanics rule selects the worldvolume-volume member
of the previously classified first-jet interface-action family.  This module
keeps the FSC symbolic, uses no measured constant, and does not evaluate the
still-independent Gate-7 certificate.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np


ACTION_VERSION = "BHSM-AE-3.2.16-COVARIANT-BUBBLE-INTERFACE-MECHANICS"
STATUS = "MINIMAL_COVARIANT_MEMBRANE_LAW_DERIVED_ON_REGULAR_STRATA"


def interface_stiffness(
    alpha_fsc: float, scale_length: float, worldvolume_dimension: int
) -> float:
    """Return gamma=alpha_FSC ell^(-m) in hbar=1 units.

    ``alpha_fsc`` is a symbolic input to the scientific payload; the numerical
    helper exists only for dimensional and regression checks.
    """
    if alpha_fsc <= 0.0:
        raise ValueError("alpha_fsc must be positive")
    if scale_length <= 0.0:
        raise ValueError("scale_length must be positive")
    if worldvolume_dimension < 1:
        raise ValueError("worldvolume_dimension must be positive")
    return float(alpha_fsc / scale_length**worldvolume_dimension)


def curvature_traction(gamma: float, principal_curvatures: Iterable[float]) -> float:
    """Return the oriented Young--Laplace normal traction gamma*K."""
    if gamma < 0.0:
        raise ValueError("gamma must be nonnegative")
    return float(gamma * math.fsum(float(value) for value in principal_curvatures))


def relativistic_radial_membrane_traction(
    gamma: float,
    spatial_surface_dimension: int,
    radius: float,
    normal_velocity: float,
    normal_acceleration: float,
) -> float:
    """Return the exact per-area left side of the spherical membrane equation.

    It follows from ``L=-gamma*Omega_p*R**p*sqrt(1-Rdot**2)``.  No bulk
    impedance or outgoing flux is hidden in this surface contribution.
    """
    if gamma < 0.0:
        raise ValueError("gamma must be nonnegative")
    if spatial_surface_dimension < 1:
        raise ValueError("spatial_surface_dimension must be positive")
    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if abs(normal_velocity) >= 1.0:
        raise ValueError("normal_velocity must be subluminal")
    lorentz = 1.0 - normal_velocity**2
    return float(gamma * (
        normal_acceleration / lorentz**1.5
        + spatial_surface_dimension / (radius * math.sqrt(lorentz))
    ))


def spectral_formation_number(
    event_drive: float, surface_stiffness: float, environmental_impedance: float
) -> float:
    """Return the dimensionless drive/resistance quotient for one mode."""
    denominator = surface_stiffness + environmental_impedance
    if event_drive < 0.0:
        raise ValueError("event_drive must be nonnegative")
    if denominator <= 0.0:
        raise ValueError("total resistance must be positive")
    return float(event_drive / denominator)


def build_payload(
    owner_action: dict[str, Any],
    fsc: dict[str, Any],
    environment: dict[str, Any],
    moving_reset: dict[str, Any],
) -> dict[str, Any]:
    """Build the claim-bounded scientific payload from prior authorities."""
    if owner_action["classification"]["interface_freedom"] != "IF5":
        raise ValueError("the prior unselected interface class is required")
    if fsc["adjudication"]["primitive"]["classification"] != "FSC-P1":
        raise ValueError("symbolic FSC-P1 authority is required")
    if environment["ENVIRONMENTAL_CLASSIFICATION"] != (
        "E_s=(alpha_s,tau_s,I_s,Lambda_s,B_s)"
    ):
        raise ValueError("the five-component environment descriptor is required")
    if moving_reset["claim_boundary"]["R_class"] != "R4":
        raise ValueError("the prior R4 reset boundary is required")

    return {
        "artifact": "BHSM_COVARIANT_BUBBLE_INTERFACE_MECHANICS",
        "action_version": ACTION_VERSION,
        "status": STATUS,
        "authority": (
            "OWNER_SELECTED_MINIMAL_COVARIANT_BUBBLE_MECHANICS_COMPOSED_WITH_"
            "EXISTING_REGULAR_STRATUM_ACTION_AND_SYMBOLIC_FSC_REFERENCE"
        ),
        "recovered_authorities": {
            "particle": (
                "persistent topologically organized energy-geometry envelopment"
            ),
            "process_order": [
                "formation", "encapsulation", "persistence",
                "de-envelopment_or_decay", "updated_parent_or_environment",
            ],
            "prior_interface_class": "ORD1/IF5",
            "prior_reset_class": "R4",
            "environment": "E_s=(alpha_s,tau_s,I_s,Lambda_s,B_s)",
            "local_material_carrier": "Sigma_enc={sigma=0} in the owned AE3 subsystem",
        },
        "domain": {
            "regular": (
                "timelike or Euclidean regular worldvolume W_s embedded in G_A, "
                "with induced metric h_ab and oriented normal n"
            ),
            "pregeometry": (
                "no pressure, area, curvature, velocity, stress, or membrane "
                "equation is asserted on C_A"
            ),
            "transition_rule": (
                "interface mechanics starts only on the first produced regular "
                "geometric carrier"
            ),
        },
        "interface_action": {
            "equation": (
                "S_total=S_bulk,event+S_bulk,child+S_owned_boundary_corner"
                "-sum_s integral_(W_s) gamma_s dmu_h"
            ),
            "selected_density": "W_s=1 on each fixed regular environment stratum",
            "why_minimal": (
                "the induced worldvolume measure is the reparametrization-invariant "
                "local scalar density requiring only the already-authorized first "
                "embedding jet; its variation supplies curvature and inertia"
            ),
            "extra_viscosity": False,
            "phenomenological_damping": False,
            "new_bending_coefficient": False,
            "new_seam_potential": False,
            "interface_function_hand_selected": False,
            "constitutive_class_after_owner_mechanics": "FSC-IF1_MINIMAL_AREA_MEMBER",
        },
        "FSC": {
            "authority": "FSC-P1",
            "primitive": "positive symbolic alpha_FSC",
            "observed_alpha_EM_used": False,
            "exact_decimal_selected": False,
            "role": "dimensionless reference strength multiplying the selected area law",
            "not_claimed": [
                "universal electromagnetic force", "scale-independent observed alpha",
                "equal strength for every bulk interaction",
            ],
        },
        "interface_stiffness": {
            "classification": "GAMMA1",
            "formula": "gamma_BHSM^(s)=alpha_FSC*ell_s^(-m_s)",
            "m_s": "dim W_s=dim regular ambient stratum minus 1",
            "ell_s": (
                "the action-owned regular length in Lambda_s; ell_kappa is the "
                "current common reference when no finer derived scale exists"
            ),
            "dimension": "[gamma_s]=L^(-m_s) in hbar=1 units",
            "fitted_coefficient": None,
            "why_GAMMA1": (
                "the power and dimensionless FSC multiplier are fixed, while the "
                "current BHSM scale authority remains a symbolic existing normalization"
            ),
        },
        "variation": {
            "surface_stress": "S_Sigma^(ab)=-gamma_s h^(ab)",
            "covariant_balance": (
                "jump(T^(mu nu)n_nu)+nabla_a(S_Sigma^(ab)e_b^mu)=0"
            ),
            "normal_convention": "K=-n_mu H^mu for the chosen event-to-child normal",
            "normal_balance": "jump(T_nn)=gamma_s*K+I_bulk,response",
            "tangential_balance": "h_a^mu jump(T_mu_n)=D_a gamma_s",
            "constant_stratum_tangential_result": (
                "h_a^mu jump(T_mu_n)=0 when alpha_FSC and ell_s are constant on W_s"
            ),
            "matter_role": (
                "geometry, scalar, gauge, fermion, ghost, and higher-spin terms enter "
                "through the total action-derived bulk traction; no duplicate surface "
                "couplings are inserted"
            ),
            "corner_terms": "the already-owned GHY/Hayward corner completion is retained",
        },
        "moving_interface": {
            "exact_spherical_reduction": (
                "gamma_s[Rddot/(1-Rdot^2)^(3/2)+p/(R sqrt(1-Rdot^2))]"
                "=Delta P_event+P_bulk,response"
            ),
            "source_action": "L_Sigma=-gamma_s Omega_p R^p sqrt(1-Rdot^2)",
            "radius": "areal radius of an action-selected symmetric regular carrier only",
            "normal_velocity": "u_n=n_mu dX^mu/dtau",
            "inertia": "worldvolume Legendre Hessian plus action-derived bulk impedance",
            "damping": (
                "none locally; any effective loss must be the computed outward Noether "
                "or radiative flux"
            ),
            "newtonian_fluid_equation_imported": False,
        },
        "nucleation": {
            "operator": "H_form=H_bulk,constrained+gamma_s J_Sigma-H_event,drive",
            "Jacobi_operator": "J_Sigma=-Delta_Sigma-(|A|^2+Ric(n,n))",
            "criterion": "lambda_min(H_form)=0 with a simple oriented first crossing",
            "stable_side": "lambda_min(H_form)>0",
            "unstable_side": "lambda_min(H_form)<0",
            "distinctions": {
                "spectral_instability": "zero/negative constrained Hessian mode",
                "local_formation": "nonlinear branch from the crossing",
                "geometric_enclosure": "regular closed carrier solution",
                "persistent_particle": "formed branch also passes monodromy/Floquet criteria",
            },
        },
        "harmonic_modes": {
            "decomposition": "delta R=sum_lambda a_lambda Y_lambda",
            "event_ownership": (
                "the initiating event projector fixes populated channels and their owned "
                "amplitude/phase; no independent child amplitude is introduced"
            ),
            "mode_equation": (
                "I_lambda D_tau^2 a_lambda+[gamma_s j_lambda+Z_lambda]a_lambda"
                "=f_event,lambda"
            ),
            "j_lambda": "eigenvalue of the constrained Jacobi operator J_Sigma",
            "Z_lambda": "action-derived environmental/bulk impedance Hessian",
            "family_assignment_promoted": False,
            "N12_event_relabelled_as_child_harmonic": False,
        },
        "formation_number": {
            "classification": "RHO-B2",
            "definition": (
                "rho_B=sup_(psi!=0) <psi,H_event,drive psi>/"
                "<psi,(gamma_s J_Sigma+H_impedance)psi>"
            ),
            "threshold": "rho_B=1 exactly when the corresponding simple mode of H_form vanishes",
            "historical_relation": (
                "corrected operator-valued version of E_mode/E_impedance; the old scalar "
                "rho_hold is recovered only after a one-mode common-charge reduction"
            ),
            "arbitrary_energy_spacetime_ratio_introduced": False,
        },
        "environment_and_time_order": {
            "formation": (
                "(event mode,alpha_s,tau_s,I_s,Lambda_s,B_s) selects admissible "
                "regular carrier channels, scale, drive, and initial data"
            ),
            "propagation": (
                "the formed child evolves in its later local causal environment; the "
                "formation environment need not persist"
            ),
            "first_future_carrier_rule": (
                "first regular future W_s where the constrained lambda_min(H_form) has "
                "a simple oriented zero and the nonlinear branch satisfies constraints"
            ),
        },
        "carrier_reset": {
            "carrier_class": "CARR2_CONDITIONAL",
            "carrier": (
                "stationary worldvolume selected by the coupled bulk-interface equations, "
                "unique modulo reparametrization only if the constrained IVP and first "
                "crossing are proved well posed and simple"
            ),
            "F_B": (
                "the event-to-child trace map induced by the solved worldvolume flow and "
                "its spin/bundle parallel transport; not the identity by convention"
            ),
            "F_B_selected_now": False,
            "L_s_physical": (
                "q_e=C_s(F_B)q_c; Pi_c+C_s(F_B)^*Pi_e=-delta S_Sigma/delta q_c"
            ),
            "Lagrangianity": (
                "conditional on the displayed relation being the graph of the exact "
                "surface generating functional on the reduced trace space"
            ),
            "Delta_enc": (
                "Pi_c+C(F_B)^*Pi_e=-delta S_Sigma/delta q_c; its geometric normal "
                "component is gamma_s K and its tangential component is -D_a gamma_s"
            ),
            "active_support": "the solved regular worldvolume W_s",
            "active_scale": "alpha_FSC*ell_s^(-m_s)",
        },
        "persistence_and_decay": {
            "formation_is_persistence": False,
            "required_persistence_test": "existing constrained monodromy/Floquet criterion",
            "decay": (
                "forward loss of stability followed by de-envelopment and conserved "
                "outgoing/multiple-child flux; not F_B^(-1)"
            ),
            "closed": False,
        },
        "dependency": {
            "causal_order": [
                "event_environment_mode", "bubble_interface_equations",
                "first_future_carrier", "F_B_and_L_s", "moving_reset_domain",
                "Theta_xi_H_Q", "energetic_consistency",
            ],
            "constitutive_cycle_removed": True,
            "executable_LOOP_class": "LOOP3",
            "why_LOOP3_remains": (
                "the coupled full-field IVP, unique first crossing, physical F_B, and "
                "reduced operator domains are not yet instantiated"
            ),
        },
        "N12": {
            "new_independent_rank": 0,
            "residual_before_time_quotient": 67,
            "residual_after_time_quotient": 66,
            "Gate7_result_imported": False,
        },
        "claim_boundary": {
            "MINIMAL_REGULAR_COVARIANT_INTERFACE_ACTION_DERIVED": True,
            "DIMENSIONAL_FSC_STIFFNESS_LAW_DERIVED": True,
            "STRESS_JUMP_AND_MOVING_INTERFACE_EQUATIONS_DERIVED": True,
            "NUCLEATION_AND_HARMONIC_OPERATOR_LAWS_DERIVED": True,
            "PHYSICAL_CARRIER_INSTANTIATED": False,
            "PHYSICAL_F_B_INSTANTIATED": False,
            "FULL_FIELD_RESET_DOMAIN_INSTANTIATED": False,
            "PERSISTENCE_DECAY_CLOSED": False,
            "TRACK1_TWO_RADIUS_GATE7_IMPORTED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "VALIDATED": [
            "minimal regular-stratum membrane action and FSC dimensional scaling",
            "normal and tangential stress balance from total-action variation",
            "relativistic spherical moving-interface reduction without phenomenological loss",
            "constrained nucleation operator, harmonic equation, and RHO-B2 quotient",
            "action-generated conditional reset relation and active differential",
        ],
        "INVALIDATED": [
            "copying a Newtonian Rayleigh-Plesset equation into BHSM",
            "fitted surface tension, viscosity, damping, or FSC exponent",
            "ordinary bubble variables on C_A",
            "identity attachment or independently selected child amplitude",
            "formation automatically implies persistence",
        ],
        "REDUNDANT": [
            "a duplicate GHY/Hayward coefficient",
            "an arbitrary IF5 response function after the owner selects minimal membrane mechanics",
            "a separate scalar energy/spacetime ratio definition",
        ],
        "OPEN": [
            (
                "COUPLED_CONSTRAINT_REDUCED_FULL_FIELD_INTERFACE_IVP_WITH_A_PROVED_"
                "UNIQUE_SIMPLE_FIRST_CROSSING_AND_INDUCED_SPIN_BUNDLE_RESET_MAP"
            )
        ],
        "exact_next_object": (
            "COUPLED_CONSTRAINT_REDUCED_FULL_FIELD_INTERFACE_IVP_WITH_A_PROVED_"
            "UNIQUE_SIMPLE_FIRST_CROSSING_AND_INDUCED_SPIN_BUNDLE_RESET_MAP"
        ),
        "FULL_BHSM_COMPLETE": False,
    }
