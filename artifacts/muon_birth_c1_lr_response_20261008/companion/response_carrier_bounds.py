#!/usr/bin/env python3
"""Exact rational carrier interior/extension bounds from retained source decimals.

The results describe the existing one-channel positive carrier at z=-1.
The LR perturbation norm is not supplied. Its threshold is a sufficient
conditional criterion for a bounded operator on the normalized bulk L2 space,
perturbing the same quadratic form and domain. A merely H1-relative form does
not meet that hypothesis. The perturbation is not identified with a literal
LR mass matrix.
"""

from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
import json


def decimal_bound(q, *, direction, digits=80):
    with localcontext() as context:
        context.prec = digits
        context.rounding = direction
        return str(Decimal(q.numerator)/Decimal(q.denominator))


def record(q):
    return {
        "exact_fraction": str(q),
        "decimal_lower_80_digits": decimal_bound(q, direction=ROUND_FLOOR),
        "decimal_upper_80_digits": decimal_bound(q, direction=ROUND_CEILING),
    }


def compute():
    lam = F("1.33025636847111862e-30")
    raw_a = F("1051216787836407.6")
    edge_t = F("1.8602143121971425e-45")
    s = F("1.5076638829955453")
    k2 = F(1)
    a = max(raw_a, edge_t/(lam*lam))
    t = a*lam*lam
    st = s*t
    if not (4*st < 1 and st < F(3, 2)):
        raise ValueError("Retained rational bound hypotheses fail")
    b = t/(1-4*st)
    d = t*t/((3-st)**2+k2*t*t)
    # This envelope deliberately drops the positive kappa^2 denominator term.
    e2 = t*(1+st+(s*s+k2)*t*t/3)/(F(3, 2)-st)**2
    threshold = 1/(d+b*e2)
    # For a possibly singular family ||V(lambda)|| <= vhat/lambda^4, retain
    # conservative coefficient bounds valid at EVERY positive family member.
    dc = a*a/(3-st)**2
    bc = a/(1-4*st)
    ec = a*(1+st+(s*s+k2)*t*t/3)/(F(3, 2)-st)**2
    scaled_threshold = 1/(dc+bc*ec)
    values = {
        "effective_a_upper": a,
        "T_star": t,
        "S_T_star": st,
        "seam_inverse_b_star": b,
        "interior_Dirichlet_inverse_d_star": d,
        "bulk_L2_Poisson_extension_norm_squared_e_star": e2,
        "b_star_times_e_star_squared": b*e2,
        "inverse_seam_LR_derivative_prefactor_b2_e2": b*b*e2,
        "d_star_plus_b_star_times_e_star_squared": d+b*e2,
        "sufficient_uniform_V_norm_threshold": threshold,
        "interior_inverse_over_lambda4_coefficient": dc,
        "seam_inverse_over_lambda2_coefficient": bc,
        "extension_norm_squared_over_lambda2_coefficient": ec,
        "inverse_seam_LR_derivative_over_lambda6_coefficient": bc*bc*ec,
        "sufficient_lambda4_V_norm_threshold": scaled_threshold,
    }
    for q in values.values():
        lo = F(decimal_bound(q, direction=ROUND_FLOOR))
        hi = F(decimal_bound(q, direction=ROUND_CEILING))
        if not lo <= q <= hi:
            raise AssertionError("Outward decimal rounding failed")
    return {
        "classification": "DERIVED_CARRIER_BOUNDS_AND_CONDITIONAL_SAME_FORM_PERTURBATION_CRITERION",
        "scope": "retained |mu|=3/2 product channel, z=-1, 0<lambda<=lambda_star",
        "channel_scope_of_perturbation": "V acts within the retained channel or an independently verified closed sector covered by these bounds",
        "reference_commit": "ad750077f1a3138418a2dc4ee65f7c50236b5608",
        "source_paths": [
            "artifacts/flagship_integration/BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json",
            "artifacts/flagship_integration/BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json",
        ],
        "source_decimal_inputs": {
            "lambda_star": "1.33025636847111862e-30",
            "original_a_upper": "1051216787836407.6",
            "edge_duration_upper": "1.8602143121971425e-45",
            "superpotential_upper": "1.5076638829955453",
            "kappa_squared": "1",
        },
        "domain": "bulk proper-time L2; zero-trace interior H_0^1; Poisson lift u(0)=0,u(T)=b",
        "form": "q0[u]=integral_0^T (|(partial_tau+W)u|^2+kappa^2|u|^2) d_tau",
        "effective_a_construction": "max(original_a_upper,edge_duration_upper/lambda_star^2)",
        "unselected_uniform_family": True,
        "V_must_be_verified_on_same_quadratic_form_and_domain": True,
        "V_norm_space": "operator norm on normalized proper-time bulk L2; not merely H1-relative form norm",
        "physical_LR_V_norm_evaluated": False,
        "values": {name: record(q) for name, q in values.items()},
    }


if __name__ == "__main__":
    print(json.dumps(compute(), indent=2))
