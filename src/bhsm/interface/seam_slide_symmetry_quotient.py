"""BHSM v6.16.0 finite seam-slide and interface-quotient audit.

The module separates the first normal jet of a collar gluing extension from
the Z2-compatible average of the two outward threading traces.  It then tests
the minimal finite field transformation that changes the latter.  The
transformation is presymplectic-null as a multiplier variation but is not an
action symmetry: nonconstant seam potentials change the extrinsic curvature
and carry a quadratic P1 action cost.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import sympy as sp


VERSION = "v6.16.0"
SPRINT = "bhsm-seam-slide-symmetry-quotient-v6-16-0"
SOURCE_MAIN_SHA = "5c5bec4a0534b37b51a010b171d8fbccb068b1ac"
V615_HEAD_SHA = "2437eda6ff1777a182de3222bf40f1ac20c85412"

PRIMARY_RESULT = "BHSM_SEAM_SLIDE_HAS_NONZERO_HIGHER_ORDER_ACTION_COST"
JET_RESULT = "BHSM_SEAM_THREADING_IS_NOT_THE_FIRST_NORMAL_GLUE_JET"
CORE_RESULT = "BHSM_CORE_CONTACT_FUNCTIONAL_NOT_PRESENT_IN_FROZEN_ACTION"
SHORTCUT_RESULT = "BHSM_ZERO_THREADING_SHORTCUT_REMAINS_REJECTED"
NOETHER_RESULT = "BHSM_SEAM_SLIDE_HAS_NO_FIRST_CLASS_GENERATOR"

ARTIFACT_FILES = {
    "gluing": "BHSM_seam_slide_gluing_jet_and_finite_map_v6_16_0.json",
    "audit": "BHSM_seam_slide_action_observable_noether_audit_v6_16_0.json",
    "verdict": "BHSM_v6_16_0_seam_slide_quotient_verdict.json",
}

GUARDS = {
    "new_action_term": False,
    "anchoring_potential": False,
    "anchoring_coefficient": False,
    "new_numerical_primitive": False,
    "new_dimensionful_primitive": False,
    "arbitrary_S_Sigma_condition": False,
    "boundary_tension": False,
    "tau_J": False,
    "radion_potential": False,
    "measured_input": False,
    "neutral_work": False,
    "physical_bulk_Dirac_law": False,
    "Green_operator_constructed": False,
    "fold_kinetic_evaluated": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "metric_assigned_to_common_core": False,
}

S_PLUS, S_MINUS = sp.symbols("S_out_plus S_out_minus", real=True)
LAMBDA = sp.symbols("lambda", real=True)
N = sp.symbols("N", real=True, positive=True)
A = sp.symbols("a", real=True, positive=True)


def glue_jet_potential(
    s_out_plus: sp.Expr = S_PLUS, s_out_minus: sp.Expr = S_MINUS
) -> sp.Expr:
    """Longitudinal first-normal glue-jet potential.

    Pulling the minus ADM collar metric back by
    (y,x)_+ -> (-y,Phi_y(x))_- gives
    V_mu=N_{+,mu}+N_{-,mu} in signed collar orientations.  Since
    S_common,+=S_out,+ and S_common,-=-S_out,-, the gauge-completed scalar
    relation is lambda_jet=S_out,+-S_out,- up to an irrelevant constant.
    """
    return sp.expand(s_out_plus - s_out_minus)


def threading_average(
    s_out_plus: sp.Expr = S_PLUS, s_out_minus: sp.Expr = S_MINUS
) -> sp.Expr:
    """The surviving Z2-compatible outward threading trace."""
    return sp.expand((s_out_plus + s_out_minus) / 2)


def z2_reduce_gluing_data(s: sp.Expr) -> dict[str, sp.Expr]:
    """Evaluate glue jet and average on S_out,+=S_out,-=s."""
    return {
        "glue_jet_potential": sp.simplify(glue_jet_potential(s, s)),
        "threading_average": sp.simplify(threading_average(s, s)),
    }


def seam_slide_outward(
    s_out_plus: sp.Expr,
    s_out_minus: sp.Expr,
    parameter: sp.Expr,
) -> tuple[sp.Expr, sp.Expr]:
    """Minimal Z2-compatible finite shift of the outward trace average."""
    return (
        sp.expand(s_out_plus + parameter),
        sp.expand(s_out_minus + parameter),
    )


def seam_slide_common(
    s_common_plus: sp.Expr,
    s_common_minus: sp.Expr,
    parameter: sp.Expr,
) -> tuple[sp.Expr, sp.Expr]:
    """The same slide in one common-normal orientation."""
    return (
        sp.expand(s_common_plus + parameter),
        sp.expand(s_common_minus - parameter),
    )


def compose_parameters(first: sp.Expr, second: sp.Expr) -> sp.Expr:
    """Composition law for the minimal additive field map."""
    return sp.expand(first + second)


def inverse_parameter(parameter: sp.Expr) -> sp.Expr:
    return -parameter


def delta_extrinsic_curvature(
    hessian: sp.MatrixBase, lapse: sp.Expr = N
) -> sp.ImmutableMatrix:
    """delta K_ij for delta N_i=D_i lambda at fixed h,N."""
    matrix = sp.Matrix(hessian)
    if matrix.rows != matrix.cols:
        raise ValueError("hessian must be square")
    return sp.ImmutableMatrix(-matrix / lapse)


def delta_Q(
    hessian: sp.MatrixBase, lapse: sp.Expr = N
) -> sp.ImmutableMatrix:
    """Flat-frame delta(K_ij-K delta_ij) for the seam candidate."""
    matrix = sp.Matrix(hessian)
    if matrix.rows != matrix.cols:
        raise ValueError("hessian must be square")
    identity = sp.eye(matrix.rows)
    return sp.ImmutableMatrix((-matrix + sp.trace(matrix) * identity) / lapse)


def shift_quadratic_density(
    hessian: sp.MatrixBase, lapse: sp.Expr = N
) -> sp.Expr:
    """Quadratic change in K_ij K^ij-K^2 at fixed h,N."""
    matrix = sp.Matrix(hessian)
    if matrix.rows != matrix.cols:
        raise ValueError("hessian must be square")
    norm_squared = sp.trace(matrix.T * matrix)
    return sp.simplify((norm_squared - sp.trace(matrix) ** 2) / lapse**2)


def s3_harmonic_integrated_density(
    harmonic_number: int, radius: sp.Expr = A
) -> sp.Expr:
    """Integrated density coefficient per int(lambda^2) on round S3.

    The Bochner identity gives
    int[(D_iD_j lambda)^2-(Delta lambda)^2]
    =-int Ric(D lambda,D lambda).
    """
    if harmonic_number < 0:
        raise ValueError("harmonic_number must be nonnegative")
    ell = sp.Integer(harmonic_number)
    return sp.simplify(-2 * ell * (ell + 2) / radius**4)


def source_and_provenance_ledger() -> dict[str, Any]:
    return {
        "sources_inspected": [
            "v6.1.4 exact Z2 double-cap junction",
            "v6.1.7 scalar-wall Puiseux fold",
            "v6.12 radial ADM constraint obstruction",
            "v6.13 fixed-iota endpoint domain",
            "v6.14 conditional composite support",
            "v6.15 Z2 symplectic threading domain",
            "v6.2 advanced-state adopted ontology",
            "v6.1.3 P1+GHY+B1+metric-matching action",
            "v5.12 core-source and collar-action audit",
        ],
        "stored_action": {
            "P1": "explicit",
            "GHY": "explicit",
            "bulk_scalar": "explicit",
            "intrinsic_B1": "explicit provisional axiom",
            "metric_matcher": "explicit",
            "core_contact_functional": None,
        },
        "stored_domain": {
            "fixed_B1_embedding": "explicit",
            "Z2_cap_exchange": "explicit",
            "fixed_interface_map": "identity up to B1 coordinates",
            "first_normal_glue_jet": "not declared as physical data",
            "seam_slide_group": None,
        },
        "core_doctrine": {
            "stored_statement": "common core is non-spatiotemporal",
            "status": "Adopted BHSM axiom",
            "metric": None,
            "distance": None,
            "duration": None,
            "density": None,
            "ordinary_inside_outside": None,
            "core_transfer_mechanism": None,
        },
        "core_contact_functional_present": False,
        "uniform_contact_statement": (
            "candidate coefficient-free BHSM identification, not a stored "
            "action or domain theorem"
        ),
        "result": CORE_RESULT,
    }


def provenance_ledger() -> list[dict[str, str]]:
    return [
        {
            "item": "collar gluing and vector-field flow",
            "status": "Adopted from established physics/mathematics",
        },
        {
            "item": "P1+GHY+B1+metric matcher and fixed Z2 domain",
            "status": "Adopted BHSM axiom",
        },
        {
            "item": "common core is non-spatiotemporal",
            "status": "Adopted BHSM axiom",
        },
        {
            "item": "uniform core contact independent of S_Sigma",
            "status": "BHSM identification",
        },
        {
            "item": "glue jet is the trace difference, not its average",
            "status": "Derived consequence",
        },
        {
            "item": "quadratic P1 cost for nonconstant seam potential",
            "status": "Derived consequence",
        },
        {
            "item": "zero-threading quotient representative",
            "status": "Rejected by calculation",
        },
        {
            "item": "threading-domain axiom or operator boundary condition",
            "status": "Active construction target",
        },
    ]


def variable_separation_ledger() -> dict[str, Any]:
    return {
        "wall_position": {
            "variable": "zeta(x)",
            "role": "moves B1 support",
        },
        "fold_amplitude": {
            "variable": "q(x)",
            "role": "changes scalar wall and cap solution",
            "current_status": "static fold coordinate, not certified 4D field",
        },
        "threading": {
            "variable": "S_Sigma(x)",
            "role": "gauge-invariant radial-shift/longitudinal trace",
        },
        "minimal_seam_candidate": {
            "delta_zeta": 0,
            "delta_q": 0,
            "delta_scalar_support": 0,
            "delta_S_Sigma": "lambda",
        },
        "wall_translation_is_seam_slide": False,
        "composite_support_implication": (
            "fixing zeta with sigma_hat still leaves S_Sigma unchanged"
        ),
    }


def gluing_jet_ledger() -> dict[str, Any]:
    return {
        "collars": {
            "U_+": "[-epsilon,0] x Sigma",
            "U_-": "[0,+epsilon] x Sigma",
        },
        "map": "(y,x)_+ ~ (-y,Phi_y(x))_-",
        "zeroth_jet": "Phi_0=phi_Sigma=id in the frozen B1 coordinates",
        "first_jet": "V^mu=partial_y Phi_y^mu|0",
        "decomposition": "V^mu=D^mu lambda_jet+V_T^mu",
        "metric_pullback": (
            "dx_-^mu+N_-^mu dy_-="
            "dx^mu+(V^mu-N_-^mu)dy at y=0"
        ),
        "cross_metric_relation": "V_mu=N_+,mu+N_-,mu",
        "gauge_completed_scalar_relation": {
            "common": "lambda_jet=S_common,++S_common,-",
            "outward": "lambda_jet=S_out,+-S_out,-",
            "normalization": "V^mu=D^mu lambda_jet",
        },
        "Z2": {
            "relation": "S_out,+=S_out,-",
            "glue_jet": 0,
            "free_average": "S_bar=(S_out,++S_out,-)/2",
        },
        "first_jet_controls_unresolved_trace": False,
        "collar_extension_status": (
            "Phi_y beyond Phi_0 is a noncanonical collar extension unless "
            "separately promoted to physical domain data"
        ),
        "result": JET_RESULT,
    }


def infinitesimal_candidate_ledger() -> dict[str, Any]:
    return {
        "definition_outward": (
            "delta_lambda S_out,+=delta_lambda S_out,-=lambda"
        ),
        "definition_common": (
            "delta_lambda S_common,+=lambda; "
            "delta_lambda S_common,-=-lambda"
        ),
        "minimal_field_laws": {
            "B_common,+": "+lambda times a smooth collar extension",
            "B_common,-": "-lambda times its reflected extension",
            "E": 0,
            "zeta": 0,
            "q": 0,
            "N": 0,
            "h_mu_nu_trace": 0,
            "bulk_sigma": 0,
            "intrinsic_B1_fields": 0,
            "matching_multiplier": 0,
            "common_normal": 0,
        },
        "induced_metric": "unchanged at fixed support",
        "scalar_pullback": "unchanged",
        "normal_shift": "delta N_mu=D_mu lambda in each outward convention",
        "extrinsic_curvature": (
            "delta K_mu_nu=-(1/N)D_muD_nu lambda at the interface"
        ),
        "Q_jump": "changed generically for nonconstant lambda",
        "boundary_stress": "intrinsic B1 stress unchanged",
        "old_diffeomorphism": False,
        "reason_not_old_gauge": (
            "the declared radial/tangential diffeomorphisms leave S_Sigma invariant"
        ),
        "classification": (
            "Z2-compatible change of the radial-shift multiplier boundary "
            "trace; not the collar glue-jet automorphism"
        ),
        "preserves_all_attempted_data": False,
    }


def finite_map_ledger() -> dict[str, Any]:
    return {
        "T_lambda": (
            "(S_out,+,S_out,-)->(S_out,++lambda,S_out,-+lambda), "
            "with a smooth reflected bulk extension of delta B"
        ),
        "identity": "T_0=id",
        "composition": "T_lambda1 T_lambda2=T_(lambda1+lambda2)",
        "inverse": "T_lambda^-1=T_-lambda",
        "domain": (
            "maps the broad off-shell fixed-Z2 multiplier domain to itself "
            "when the extension is smooth and regular"
        ),
        "extension_uniqueness": False,
        "extension_requirement": (
            "profile equals one at Sigma and can be chosen to vanish near both poles"
        ),
        "Z2": "preserved by reflected signs in common orientation",
        "topology_change": False,
        "normal_bundle_holonomy": False,
        "caustics": "not applicable to the additive field map",
        "metric_nondegeneracy": (
            "ADM determinant is independent of shift; N and h remain fixed"
        ),
        "constant_spacetime_lambda": (
            "D_mu lambda=0, so it is a trivial scalar-potential stabilizer"
        ),
        "local_lambda": "globally definable as a field map but changes geometry",
        "spatial_harmonics": {
            "ell=0_time_independent": "trivial stabilizer",
            "ell>=1": "nonzero Hessian and action cost",
            "ell=0_time_dependent": "nontrivial through D_time lambda",
        },
        "compact_S3": (
            "smooth lambda and collar extensions exist globally; compactness "
            "does not remove the action obstruction"
        ),
        "collar_flow_candidate": {
            "map": "Phi_y=Flow_y(D lambda)",
            "local_and_compact_global_flow": True,
            "arbitrary_gradient_family_closed_under_composition": False,
            "reason": (
                "[D lambda_1,D lambda_2] is not generally a gradient"
            ),
            "acts_on": "lambda_jet=S_out,+-S_out,-, not S_bar",
        },
        "finite_group_of_action_symmetries": False,
    }


def action_audit_ledger() -> dict[str, Any]:
    return {
        "candidate": "minimal T_lambda with h,N,E,zeta,sigma fixed",
        "P1_plus_GHY": {
            "off_shell": "not invariant",
            "delta_K": "-N^-1 D_muD_nu lambda",
            "linear": (
                "A1 is the momentum-constraint contraction plus tangential "
                "and radial endpoint divergences"
            ),
            "quadratic": (
                "A2 contains (kappa_1/2) integral N sqrt|h| N^-2 "
                "[(D_muD_nu lambda)^2-(D^2 lambda)^2]"
            ),
        },
        "GHY_separate": (
            "delta K=-N^-1 D^2 lambda; it is a closed-slice divergence only "
            "under the corresponding homogeneous coefficient assumptions"
        ),
        "bulk_scalar": {
            "off_shell": (
                "n sigma changes by -N^-1 D^mu lambda D_mu sigma, so the "
                "scalar action is not invariant for a general off-shell field"
            ),
            "static_fold": "invariant because D_mu sigma=0",
        },
        "intrinsic_B1": "exactly unchanged when intrinsic fields and h are fixed",
        "metric_matcher": (
            "fixed-support induced metric remains h, so the algebraic matching "
            "constraint is unchanged"
        ),
        "Z2_factor": "preserved",
        "stored_core_or_topological_contact_term": None,
        "invariance_levels": {
            "fully_off_shell": False,
            "after_metric_matching": False,
            "after_bulk_constraints_linear_order": True,
            "after_junction_linear_order": True,
            "static_fold_linear_order": True,
            "static_fold_quadratic_order": False,
        },
        "first_possible_nonzero_order_on_solution": 2,
        "round_S3_Bochner_test": (
            "for a time-independent ell harmonic, integral[(Hess lambda)^2"
            "-(Delta lambda)^2]=-2 ell(ell+2)a^-4 integral lambda^2"
        ),
        "nonzero_for": "every nonconstant spatial scalar harmonic ell>=1",
        "strongest_invariance": (
            "linearized on-constraint degeneracy only; lifted by quadratic "
            "P1 cost"
        ),
        "anchoring_term_added": False,
        "result": PRIMARY_RESULT,
    }


def uniform_core_contact_ledger() -> dict[str, Any]:
    return {
        "abstract_candidate": (
            "C_core[gamma,topology,orientation class,conserved charges,"
            "scalar-wall support,allowed interface invariants]"
        ),
        "proposed_condition": "partial C_core/partial S_Sigma=0",
        "stored_functional": False,
        "derived_from_action": False,
        "follows_from_absence_of_action_dependence": False,
        "admissible_coefficient_free_identification": True,
        "conflicts_with_nonspatiotemporal_core": False,
        "inserted_into_action": False,
        "metric_assigned_to_core": False,
        "sufficient_to_derive_T_lambda": False,
        "reason_insufficient": (
            "it declares one undefined contact label insensitive to threading "
            "but does not erase the bulk K, Q, curvature, and action changes"
        ),
        "action_blindness_equals_physical_equivalence": False,
        "status": "BHSM identification",
        "adopted": False,
    }


def observable_ledger() -> dict[str, Any]:
    return {
        "induced_metric": "exactly invariant",
        "intrinsic_curvature": "exactly invariant",
        "bulk_curvature_invariants": "changed generically",
        "one_sided_extrinsic_curvature": "changed for nonconstant lambda",
        "Q_jump": "changed for nonconstant lambda",
        "scalar_pullback": "exactly invariant",
        "scalar_normal_derivative": (
            "changed off shell when D_mu sigma is nonzero; invariant on the "
            "homogeneous static fold"
        ),
        "scalar_wall_zero_set": "exactly invariant",
        "zeta": "exactly invariant",
        "q": "exactly invariant",
        "tau": "exactly invariant",
        "scalar_sign_s": "exactly invariant",
        "matching_multiplier_after_elimination": "not a physical observable",
        "intrinsic_boundary_stress": "exactly invariant",
        "intrinsic_conserved_charges": "exactly invariant",
        "bulk_gravitational_charge_change": "not evaluated",
        "topology": "exactly invariant",
        "orientation": "exactly invariant",
        "M4_confined_causal_relations": "exactly invariant because h is fixed",
        "bulk_causal_relations": "changed generically",
        "intrinsic_Wilson_holonomy_data": "exactly invariant when relevant",
        "action_derived_intrinsic_currents": "exactly invariant",
        "stored_core_contact_label": "undefined",
        "conditional_uniform_contact_label": "invariant by proposed definition",
        "frozen_predictions": "exactly invariant",
        "distinguishing_declared_data_exist": True,
        "exact_quotient_observable_test_passed": False,
    }


def noether_ledger() -> dict[str, Any]:
    return {
        "interface_presymplectic": (
            "i_(partial/partial S_Sigma) Omega_Sigma=0 from v6.15"
        ),
        "nonlinear_extended_ADM_presymplectic": (
            "a pure lapse/shift multiplier variation remains null because "
            "the multiplier has no radial canonical momentum"
        ),
        "candidate_generator_for_multiplier_shift": "G_multiplier[lambda]=0",
        "zero_generator_implies_gauge": False,
        "reason": (
            "the multiplier-only vector is not tangent to the nonlinear "
            "solution space and is not a symmetry of the action"
        ),
        "actual_momentum_generator": (
            "G_diff[xi]=integral_C xi^mu C_mu plus its allowed boundary term"
        ),
        "actual_generator_action_on_S": "delta_xi S_Sigma=0",
        "new_Noether_identity": False,
        "new_first_class_constraint": False,
        "boundary_charge": None,
        "reducibility_identity": False,
        "linear_null_direction_integrable_as_gauge": False,
        "classification": (
            "auxiliary multiplier null direction with quadratic action "
            "lifting, not a first-class interface redundancy"
        ),
        "result": NOETHER_RESULT,
    }


def classification_ledger() -> dict[str, Any]:
    return {
        "exact_interface_redundancy": False,
        "global_on_shell_degeneracy": False,
        "physical_flat_modulus": False,
        "accidental_linearized_null": True,
        "domain_label_remains": True,
        "higher_order_lifting": True,
        "first_lifting_order": 2,
        "classification": (
            "the interface trace is presymplectic-null as an auxiliary "
            "multiplier/domain datum, but the proposed nonconstant finite "
            "slide changes Q and has quadratic action cost"
        ),
        "primary_result": PRIMARY_RESULT,
    }


def quotient_ledger() -> dict[str, Any]:
    return {
        "quotient_adopted": False,
        "equivalence_relation": None,
        "reason": (
            "T_lambda is not an action symmetry and changes declared geometric data"
        ),
        "candidate_orbit": (
            "{(S_out,++lambda,S_out,-+lambda)} is a field-map family, "
            "not a physical equivalence orbit"
        ),
        "stabilizer": "spacetime-constant lambda with D_mu lambda=0",
        "local_slice": None,
        "residual_group": None,
        "Jacobian": None,
        "S_Sigma_zero_slice_valid": False,
        "S_Sigma_zero_status": (
            "would remain an arbitrary interface condition, not a representative"
        ),
        "result": SHORTCUT_RESULT,
    }


def threading_and_fold_ledger() -> dict[str, Any]:
    return {
        "unresolved_interface_trace_count_before": 1,
        "unresolved_interface_trace_count_after": 1,
        "Green_operator_domain_ready": False,
        "representative_condition": None,
        "expected_kernel_count": None,
        "fold_route": "paused",
        "q_as_certified_4D_field": False,
        "uniform_core_contact_required_for_current_verdict": False,
        "uniform_core_contact_if_adopted": (
            "insufficient by itself to remove the bulk action obstruction"
        ),
        "exact_next_input": (
            "derive an action/domain boundary condition for S_Sigma or enlarge "
            "the theory with an explicitly adopted equivalence theorem that "
            "also removes the bulk Q and action distinctions"
        ),
        "k_q_E": None,
        "B_ext_E": None,
        "B_core_E": None,
        "m_ext_squared": None,
        "m_core_squared": None,
    }


def integrity_ledger() -> dict[str, Any]:
    return {
        "preserved": {
            "v6_15": "BHSM_Z2_SYMPLECTIC_FLUX_LEAVES_ONE_INTERFACE_TRACE",
            "S_gauge_status": (
                "gauge invariant under already declared diffeomorphisms"
            ),
            "fixed_action_condition": None,
            "composite_support_condition": "fixes zeta, not S_Sigma",
            "canonical_momentum_S": 0,
            "interface_flux_for_reflection_compatible_S": 0,
            "unresolved_interface_trace_count": 1,
            "q_status": "static fold coordinate",
            "F0_equals_M4_squared": "pi/2",
            "K_scalar": ">=2>0",
            "K_Weyl": "3 chi_1^2(4-pi)^2/(16 pi)>0",
        },
        "guards": dict(GUARDS),
    }


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "v6_15_head_sha": V615_HEAD_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "gluing": {
            **_common("BHSM_seam_slide_gluing_jet_and_finite_map_v6_16_0"),
            "source_and_provenance": source_and_provenance_ledger(),
            "provenance": provenance_ledger(),
            "variables": variable_separation_ledger(),
            "gluing_jet": gluing_jet_ledger(),
            "infinitesimal_candidate": infinitesimal_candidate_ledger(),
            "finite_map": finite_map_ledger(),
        },
        "audit": {
            **_common(
                "BHSM_seam_slide_action_observable_noether_audit_v6_16_0"
            ),
            "action": action_audit_ledger(),
            "core_contact": uniform_core_contact_ledger(),
            "observables": observable_ledger(),
            "Noether": noether_ledger(),
        },
        "verdict": {
            **_common("BHSM_v6_16_0_seam_slide_quotient_verdict"),
            "classification": classification_ledger(),
            "quotient": quotient_ledger(),
            "threading_and_fold": threading_and_fold_ledger(),
            "integrity": integrity_ledger(),
        },
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def artifact_bytes() -> dict[str, bytes]:
    payloads = artifact_payloads()
    return {
        ARTIFACT_FILES[key]: deterministic_json(payload).encode("utf-8")
        for key, payload in payloads.items()
    }


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for filename, content in artifact_bytes().items():
        path = target / filename
        path.write_bytes(content)
        paths.append(path)
    return paths
