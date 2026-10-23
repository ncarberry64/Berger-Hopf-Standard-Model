"""Companion parametric carrier/seam cotangent audit on incoming C1/E1.

The retained carrier family is sufficient for uniform seam-inverse transport.
It does not make an unenclosed incoming lower-order action variation zero, and
never changes the existing point-valued six-input guard or selects a member.
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
from pathlib import Path

import sympy as sp

from bhsm.interface.muon_birth_parametric_carrier_bounds import (
    retained_carrier_bound_inputs, uniform_carrier_majorants,
)

STARTING_HEAD = "60a6078844d08c0b101462eb712afbae8c12a739"
ARTIFACT_DIRECTORY = "artifacts/muon_birth_parametric_fermion_seam_20261008"
ADJOINT_PATH = "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json"
QUOTIENT_PATH = "artifacts/flagship_integration/BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json"


def fraction_record(value: Fraction) -> dict:
    """Serialize an exact majorant and an outward decimal enclosure."""
    if not isinstance(value, Fraction):
        raise TypeError("Exact Fraction required")
    endpoints = []
    for rounding in (ROUND_FLOOR, ROUND_CEILING):
        with localcontext() as context:
            context.prec = 80
            context.rounding = rounding
            endpoints.append(str(Decimal(value.numerator)/Decimal(value.denominator)))
    return dict(exact=str(value), decimal_enclosure=endpoints,
                decimal_precision=80, rounding="FLOOR,CEILING")


def seam_cotangent_majorants(carrier_bounds: dict[str, Fraction]) -> dict[str, Fraction]:
    """Transport the supplied cotangent norm through the certified carrier seam.

    Sv=r, S^dagger p=g imply <g,Dv>=<p,Dr-(DS)v>. The constants
    multiply norm(g), norm(g)*norm(r), or norm(DS), respectively;
    they do not insert a physical source, unit cotangent or readout.
    """
    b = carrier_bounds["seam_inverse_upper"]
    if not isinstance(b, Fraction) or b <= 0:
        raise ValueError("Positive exact seam inverse bound required")
    return dict(dual_solve_norm_upper=b,
                inverse_cotangent_norm_upper=b*b,
                signed_seam_derivative_norm_factor=b*b)


def completion_inverse_upper(carrier_inverse_upper: Fraction,
                             relative_correction_upper: Fraction | None):
    """Extend coercivity only with an owned relative correction bound <1.

    For R on the common pairing/domain, rho bounds
    norm(S_car^(-1/2) R S_car^(-1/2)); unknown rho remains None.
    """
    if not isinstance(carrier_inverse_upper, Fraction) or carrier_inverse_upper <= 0:
        raise ValueError("Positive exact carrier inverse bound required")
    if relative_correction_upper is None:
        return None
    if not isinstance(relative_correction_upper, Fraction):
        raise TypeError("Relative correction bound must be an exact Fraction")
    if not 0 <= relative_correction_upper < 1:
        raise ValueError("Completion requires 0 <= relative bound < 1")
    return carrier_inverse_upper/(1-relative_correction_upper)


def exact_symbolic_seam_cotangent_identity() -> dict:
    """Check the retained implicit-adjoint contraction, not the force root."""
    inverse, derivative, dr, r, gd, pd, v = sp.symbols(
        "S_inverse D_S D_r r g_dagger p_dagger v", commutative=False)
    lhs = gd*inverse*(dr-derivative*inverse*r)
    rhs = pd*(dr-derivative*v)
    residual = sp.expand(lhs-rhs.subs({pd: gd*inverse, v: inverse*r}))
    if residual != 0:
        raise ValueError("Seam cotangent identity failed")
    return dict(residual=str(residual),
        primal="S v=r", adjoint="S^dagger p=g",
        signed_pullback="<g,Dv>=<p,Dr-(D S)v>",
        inverse_jet="D(S^-1)=-S^-1 (D S) S^-1",
        inverse_readout_cotangent="W_S=-S^(-dagger) G S^(-dagger)",
        operator_pairing="D ReTr(G^dagger S^-1)=ReTr(W_S^dagger D S)",
        physical_source_or_terminal_covector_selected=False,
        force_root_equivalence_rederived=False)


def parametric_response_packet(root: str | Path) -> dict:
    """Attach existing theorems and the audited first incoming LR obstruction."""
    root = Path(root)
    carrier = retained_carrier_bound_inputs(root)
    majorants = uniform_carrier_majorants(**{
        name: Fraction(value) for name, value in carrier["parameters"].items()})
    analytic_ratio = majorants["returned_load_to_Mf_lower_ratio_upper"]
    stored_ratio = Fraction(carrier["stored_worst_duration_sample"]["C2_load_to_incoming_lower_ratio_upper"])
    majorants["returned_load_to_Mf_lower_ratio_upper"] = max(analytic_ratio, stored_ratio)
    cotangent = seam_cotangent_majorants(majorants)
    owner = json.loads((root/ARTIFACT_DIRECTORY/"lower_order_owner_receipt.json").read_text(encoding="utf8"))
    adjoint = json.loads((root/ADJOINT_PATH).read_text(encoding="utf8"))
    quotient = json.loads((root/QUOTIENT_PATH).read_text(encoding="utf8"))
    if not adjoint["validation_passed"] or not quotient["validation_passed"]:
        raise ValueError("Validated retained adjoint/quotient records required")
    if quotient["scope"]["common_scale_quotiented"] is not False:
        raise ValueError("The common-scale component must remain physical")
    return dict(
        schema="BHSM_PARAMETRIC_INCOMING_FERMION_SEAM_RESPONSE_V1",
        starting_head=STARTING_HEAD,
        incoming_domain="C1_branch23_E1_minus",
        classification="UNIFORM_CARRIER_AND_SEAM_COTANGENT_BOUNDS__INCOMING_LR_BRIDGE_UNENCLOSED",
        desired_milestone=3,
        preserved_point_input_result=dict(operand="P_F", derivative_order=0,
            argument="parent_jet", point_value=None, guard_modified=False),
        carrier_theorem=carrier,
        retained_ratio_rounding=dict(analytic_ratio=fraction_record(analytic_ratio),
            stored_ratio=str(stored_ratio),
            uniform_reported_ratio="max(analytic majorant, retained binary64-rounded ratio)",
            stronger_physical_precision_claimed=False),
        uniform_carrier_majorants={key: fraction_record(value) for key,value in majorants.items()},
        uniform_seam_cotangent_majorants={key: fraction_record(value) for key,value in cotangent.items()},
        completed_seam_inverse_upper=completion_inverse_upper(majorants["seam_inverse_upper"], None),
        lower_order_relative_bound=None,
        parametric_decomposition=dict(
            equation="P_F(lambda,z)=P_carrier(lambda,z)+P_owned_lower_order(lambda,z)",
            carrier="M_f(lambda,z) tensor inherited_internal_identity, on the action-normalized carrier trace pairing",
            lower_order="DtN(retained complete incoming quadratic action/domain)-DtN(carrier action/domain)",
            lower_order_enclosure=None,
            boundary_response_is_not_sum_of_local_bulk_mass_matrices=True,
            total_common_pairing_bound=None),
        lower_order_owner_receipt=owner,
        symbolic_seam_cotangent=exact_symbolic_seam_cotangent_identity(),
        existing_nested_adjoint=adjoint["continuous_adjoint_theorem"],
        existing_endpoint_adjoint=adjoint["moving_endpoint_adjoint"],
        retained_time_quotient=quotient["theorem"],
        common_scale_retained_physical=True,
        complete_physical_E1_operator_enclosure=None,
        complete_CAR_projection_enclosure=None,
        uniform_state_independence=None,
        uniform_minimal_moment_rank=None,
        physical_member_selection_proved_necessary=False,
        interval_straddles_decision_boundary=False,
        decision_status="FIRST_ACTION_OWNED_LR_COTANGENT_NOT_ENCLOSED__NOT_A_STRADDLING_INTERVAL",
        first_blocker=owner["first_blocker"],
        carrier_only_Noether_scope="[M_f I,T]=0 only for channel-preserving T; not the complete consumed row",
        scalar_occupation_scope="An ordered particle scalar kernel can consume Tr(delta C); family centrality alone does not imply CAR-dual zero",
        selectors=dict(lambda_selected=False,duration_selected=False,covariance_selected=False,
                       reset_representative_selected=False),
        point_KKT_callback_called=False,
        Green_cancellation_substituted=False,
        current_C2_or_synthetic_lower_terms_transplanted=False,
        old_producers_recomputed=False,
        labels=dict(DERIVED="Rational uniform scaled-carrier/seam-inverse and cotangent norm majorants; lower-order DtN correction scope",
            EVALUATED="Retained-source identities, exact rational majorants and symbolic seam contraction",
            CONTROL_ONLY="Supplied exact algebra/projection tests",
            UNEVALUATED="Incoming LR bridge restriction/cotangent, completed parametric P_F and full consumed CAR verdict",
            OWNER_DEFINITION_GAP="No new action or selector requested; same-incoming restriction and uniform bound of a retained term remain unevaluated"),
    )
