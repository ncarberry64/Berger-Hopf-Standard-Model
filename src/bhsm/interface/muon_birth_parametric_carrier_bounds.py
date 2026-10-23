"""Exact rational majorants for the retained incoming carrier family.

This companion reuses the stored negative-axis form inequalities.  It neither
evaluates an old producer nor supplies a point-valued physical E1 KKT block.
The estimates concern the retained carrier and its nonnegative AE2 child load;
unverified lower-order and mixed fermion terms are outside their scope.
"""

from __future__ import annotations

import json
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any


COEFFICIENT_PATH = (
    "artifacts/flagship_integration/"
    "BHSM_N12_INCOMING_FINITE_AMPLITUDE_COEFFICIENT_ENCLOSURE.json"
)
NEGATIVE_AXIS_PATH = (
    "artifacts/flagship_integration/"
    "BHSM_N12_INCOMING_MF_NEGATIVE_AXIS_ENCLOSURE.json"
)


def _fraction_bound(value: Fraction, name: str, *, positive: bool) -> Fraction:
    if not isinstance(value, Fraction):
        raise TypeError(name + " must be an exact Fraction")
    if value < 0 or (positive and value == 0):
        raise ValueError(name + (" must be positive" if positive else " must be nonnegative"))
    return value


def uniform_carrier_majorants(
    *,
    a_lower: Fraction,
    a_upper: Fraction,
    lambda_upper: Fraction,
    superpotential_upper: Fraction,
    kappa_squared: Fraction = Fraction(1),
    returned_load_upper: Fraction | None = None,
) -> dict[str, Fraction]:
    """Enclose scaled M_f and seam inverse over 0<lambda<=lambda_upper.

    The retained theorem gives a_lower*lambda^2 <= T <= a_upper*lambda^2,
    exp(-4*S*T_upper)/T_upper <= M_f, and the linear-trial upper bound
    max_T[1/T+S+(S^2+kappa^2)*T/3].  For delta=4*S*a_upper*lambda_upper^2<1,
    exp(-x)>=1-x and exp(x)<=1/(1-x) give rational outward majorants.

    The unscaled M_f is only pointwise finite and has no finite uniform upper
    bound as lambda tends to zero.  Its scaled version lambda^2*M_f and the
    seam inverse have finite uniform bounds.  Unitarity and a nonnegative
    returned child load imply S_AE2>=M_f; no reset representative is selected.
    kappa_squared is one fixed negative-axis magnitude, not physical momentum.
    """
    alo = _fraction_bound(a_lower, "a_lower", positive=True)
    ahi = _fraction_bound(a_upper, "a_upper", positive=True)
    limit = _fraction_bound(lambda_upper, "lambda_upper", positive=True)
    s = _fraction_bound(superpotential_upper, "superpotential_upper", positive=False)
    k2 = _fraction_bound(kappa_squared, "kappa_squared", positive=True)
    if alo > ahi:
        raise ValueError("duration coefficient interval must be ordered")
    load = None if returned_load_upper is None else _fraction_bound(
        returned_load_upper, "returned_load_upper", positive=False
    )
    limit2 = limit * limit
    delta = 4 * s * ahi * limit2
    if delta >= 1:
        raise ValueError("rational exponential majorant requires delta < 1")
    inverse_coefficient = ahi / (1 - delta)
    inverse = inverse_coefficient * limit2
    result = {
        "delta": delta,
        "scaled_Mf_lower": (1 - delta) / ahi,
        "scaled_Mf_upper": (
            1 / alo + s * limit2 + (s * s + k2) * ahi * limit2 * limit2 / 3
        ),
        "seam_inverse_upper": inverse,
        "seam_inverse_over_lambda_squared_upper": inverse_coefficient,
    }
    if load is not None:
        result["returned_load_to_Mf_lower_ratio_upper"] = load * inverse
    return result


def _stored_fraction(value: object, name: str) -> Fraction:
    """Read a retained JSON decimal without a binary64 round trip."""
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ValueError(name + " must be a finite retained JSON number")
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError(name + " must be finite")
    return Fraction(value)


def _read_retained_json(root: Path, path: str) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = (root / path).read_bytes()
    record = json.loads(raw.decode("utf-8-sig"), parse_float=Decimal)
    if record.get("validation_passed") is not True:
        raise ValueError("Retained input was not validated: " + path)
    return record, {"path": path, "bytes": len(raw), "raw_sha256": sha256(raw).hexdigest()}


def retained_carrier_bound_inputs(
    root: str | Path,
    *,
    absolute_unit_radius_eigenvalue: Fraction = Fraction(3, 2),
    kappa_squared: Fraction = Fraction(1),
) -> dict[str, Any]:
    """Return serializable source identities and exact rational bound inputs.

    ``parameters`` contains Fraction-readable strings for
    ``uniform_carrier_majorants``. Its duration coefficient interval also
    contains the retained edge-duration rounding after exact normalization by
    lambda_upper^2. ``source_decimal_values`` preserves the original coefficient
    decimals, and raw hashes bind their original representation.
    A selected stored channel/probe is the scope of a bound, not a selected
    amplitude, duration, reset representative, covariance or physical state.
    """
    level = _fraction_bound(
        absolute_unit_radius_eigenvalue, "absolute_unit_radius_eigenvalue", positive=True
    )
    k2 = _fraction_bound(kappa_squared, "kappa_squared", positive=True)
    base = Path(root)
    coefficient, coefficient_ref = _read_retained_json(base, COEFFICIENT_PATH)
    negative_axis, negative_axis_ref = _read_retained_json(base, NEGATIVE_AXIS_PATH)
    family = coefficient["amplitude_family"]
    domain = family["parameter_domain"]
    if not isinstance(domain, str) or not domain.startswith("0<lambda<="):
        raise ValueError("Retained amplitude family must have a positive open lower endpoint")
    if domain != negative_axis["parametric_theorem"]["amplitude_domain"]:
        raise ValueError("Retained coefficient and negative-axis amplitude scopes disagree")
    limit_decimal = domain.split("<=", 1)[1]
    limit = _fraction_bound(Fraction(limit_decimal), "retained lambda_upper", positive=True)
    coefficients = family["duration_lambda_squared_coefficient_interval"]
    if len(coefficients) != 2:
        raise ValueError("Retained duration coefficient interval requires two endpoints")
    if coefficients != negative_axis["parametric_theorem"]["duration_lambda_squared_coefficient_interval"]:
        raise ValueError("Retained duration coefficient scopes disagree")
    raw_alo = _stored_fraction(coefficients[0], "original a_lower")
    raw_ahi = _stored_fraction(coefficients[1], "original a_upper")
    edge_durations = family["endpoint_proof_edge_duration_interval"]
    if len(edge_durations) != 2:
        raise ValueError("Retained edge duration interval requires two endpoints")
    edge_lo = _stored_fraction(edge_durations[0], "stored edge duration lower")
    edge_hi = _stored_fraction(edge_durations[1], "stored edge duration upper")
    if not (0 < raw_alo <= raw_ahi and 0 < edge_lo <= edge_hi):
        raise ValueError("Retained coefficient and edge duration intervals must be positive and ordered")
    edge_crosscheck = negative_axis["proof_edge_crosscheck"]
    if (edge_lo != _stored_fraction(edge_crosscheck["duration_lower"], "crosscheck duration lower")
            or edge_hi != _stored_fraction(edge_crosscheck["duration_upper"], "crosscheck duration upper")):
        raise ValueError("Retained edge duration scopes disagree")
    limit2 = limit * limit
    edge_alo = edge_lo / limit2
    edge_ahi = edge_hi / limit2
    # The original interval already applies to every positive family member.
    # Taking its envelope with the additionally rounded edge ratios only widens
    # that uniform interval; it does not select or evaluate an edge history.
    effective_alo = min(raw_alo, edge_alo)
    effective_ahi = max(raw_ahi, edge_ahi)
    rows = [row for row in negative_axis["factorized_product_Dirac_rows"] if
            _stored_fraction(row["absolute_unit_radius_eigenvalue"], "channel") == level]
    if len(rows) != 1:
        raise ValueError("Retained product-Dirac channel is absent or ambiguous")
    row = rows[0]
    probes = [probe for probe in row["negative_axis_samples"] if
              _stored_fraction(probe["kappa_squared"], "kappa_squared") == k2]
    if len(probes) != 1:
        raise ValueError("Retained negative-axis probe is absent or ambiguous")
    probe = probes[0]
    if _stored_fraction(probe["z"], "z") != -k2:
        raise ValueError("Retained probe must have z=-kappa_squared")
    load_interval = probe["C2_effective_load_interval_AE2_W_zero"]
    if len(load_interval) != 2 or _stored_fraction(load_interval[0], "returned load lower") != 0:
        raise ValueError("Retained AE2 returned-load bound must have lower endpoint zero")
    source_values = {
        "a_lower": coefficients[0],
        "a_upper": coefficients[1],
        "superpotential_upper": row["incoming_superpotential_absolute_upper"],
        "kappa_squared": probe["kappa_squared"],
        "returned_load_upper": load_interval[1],
    }
    parameters = {name: str(_stored_fraction(value, name)) for name, value in source_values.items()}
    parameters["a_lower"] = str(effective_alo)
    parameters["a_upper"] = str(effective_ahi)
    parameters["lambda_upper"] = str(limit)
    # Validate the inequality assumptions only; this is not an old producer replay.
    uniform_carrier_majorants(**{name: Fraction(value) for name, value in parameters.items()})
    stored_sample_keys = (
        "incoming_M_f_interval_at_lambda_box_edge",
        "C2_effective_load_interval_AE2_W_zero",
        "C2_load_to_incoming_lower_ratio_upper",
        "joint_seam_inverse_norm_upper",
    )
    stored_sample = {}
    for name in stored_sample_keys:
        value = probe[name]
        stored_sample[name] = ([str(_stored_fraction(item, name)) for item in value]
                               if isinstance(value, list) else str(_stored_fraction(value, name)))
    return {
        "classification": "EXACT_RATIONAL_COMPANION_INPUTS_FROM_RETAINED_CARRIER_THEOREM",
        "parameters": parameters,
        "source_decimal_values": {name: str(value) for name, value in source_values.items()} | {
            "lambda_upper": limit_decimal
        },
        "effective_duration_coefficient_provenance": {
            "classification": "UNIFORM_ENVELOPE_RETAINING_STORED_ADDITIONAL_EDGE_ROUNDING",
            "original_coefficients": {"a_lower": str(raw_alo), "a_upper": str(raw_ahi)},
            "stored_edge_duration_decimals": [str(value) for value in edge_durations],
            "stored_edge_duration_fractions": [str(edge_lo), str(edge_hi)],
            "normalizing_certified_lambda_upper": str(limit),
            "normalized_edge_coefficients": {"a_lower": str(edge_alo), "a_upper": str(edge_ahi)},
            "effective_coefficients": {"a_lower": str(effective_alo), "a_upper": str(effective_ahi)},
            "construction": (
                "a_lower_eff=min(a_lower_original,T_edge_lower/lambda_upper^2); "
                "a_upper_eff=max(a_upper_original,T_edge_upper/lambda_upper^2)"
            ),
            "provenance": (
                "Envelope retaining the stored additional edge rounding; the "
                "original uniform coefficient interval is contained, so the "
                "widened interval remains valid for every certified positive lambda."
            ),
            "source_decimal_values_are_original_coefficients": True,
            "parameters_use_effective_coefficients": True,
            "uniform_in_lambda": True,
            "physical_member_selected": False,
        },
        "source_records": [coefficient_ref, negative_axis_ref],
        "parameter_domain": domain,
        "response": "M_f=M11 after the retained zero-birth Dirichlet restriction",
        "pointwise_original_inequalities": {
            "duration": "a_lower*lambda^2 <= T(lambda) <= a_upper*lambda^2",
            "incoming_lower": "exp(-4*S*a_upper*lambda^2)/(a_upper*lambda^2) <= M_f",
            "incoming_upper": "M_f <= max_T[1/T+S+(S^2+kappa^2)*T/3] at the two duration endpoints",
            "seam": "S_AE2=M_f+U_R^dagger*M_C2*U_R >= M_f > 0",
            "inverse": "norm(S_AE2^-1) <= a_upper*lambda^2*exp(4*S*a_upper*lambda^2)",
        },
        "bound_scope": {
            "absolute_unit_radius_eigenvalue": str(level),
            "kappa_squared": str(k2),
            "z": str(-k2),
            "same_retained_product_channel_and_negative_axis_probe": True,
            "finite_retained_rows_or_channel_scope": True,
            "uniform_in_lambda": True,
            "uniform_over_all_spatial_levels_or_spectral_probes": False,
            "neutral_resolvent_probe_identified_as_physical_momentum": False,
            "complete_active_E1_fermion_operator_or_CAR_projection": False,
        },
        "stored_worst_duration_sample": stored_sample,
        "stored_maximum_sampled_returned_load_ratio": str(_stored_fraction(
            negative_axis["proof_edge_crosscheck"]["maximum_sampled_C2_load_to_incoming_lower_ratio_upper"],
            "maximum sampled ratio",
        )),
        "stored_maximum_sampled_returned_load_ratio_scope": (
            "All product-channel/probe rows recorded in the retained source; "
            "not a bound over every negative spectral probe or every spatial mode."
        ),
        "stored_spectral_probe_magnitudes": [str(_stored_fraction(p["kappa_squared"], "probe"))
                                            for p in row["negative_axis_samples"]],
        "proof_edge_role": negative_axis["proof_edge_crosscheck"]["role"],
        "unscaled_Mf_uniform_upper_finite": False,
        "scaled_Mf_uniform_bounds_finite": True,
        "seam_inverse_uniform_bound_finite": True,
        "lambda_or_duration_selected": False,
        "covariance_or_reset_representative_selected": False,
        "point_KKT_callback_called": False,
        "old_producer_recomputed": False,
        "lower_order_or_mixed_terms_defaulted_to_zero": False,
    }


__all__ = ["uniform_carrier_majorants", "retained_carrier_bound_inputs"]
