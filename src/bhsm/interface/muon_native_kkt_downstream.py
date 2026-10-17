"""Continue a supplied owner KKT impedance through the retained native chain.

This is a composition API, not a physical-data producer.  An owner identity
must identify the same action, domain, source direction and transported
support-loss branch throughout.  Every absent scalar jet and native provider
remains UNEVALUATED.  Finite controls never promote a physical Pauli number.
"""
from __future__ import annotations

from fractions import Fraction
from collections.abc import Mapping
from numbers import Number

import numpy as np

from .ae4_stratified_dirac_zeta_induced_owner import native_heat_length_squared
from .muon_native_support_loss_cutoff import (
    cutoff_from_total_contractions, lower_limit_coefficients,
)
from .universal_precision_form_factor import project_electromagnetic_form_factors


JET_KEYS = ("value", "v", "J", "vJ")
PAIRED_LEDGER = ("native_bulk_heat", "state_variation", "contact",
                 "domain_boundary", "completion_counterterm", "strong_within_native")


def _reject_intervals(value):
    """Reject interval scalars at any nesting depth before numeric conversion."""
    if type(value).__module__.startswith("flint"):
        raise TypeError("interval inputs need an interval downstream backend; no midpoint conversion")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_intervals(key)
            _reject_intervals(item)
    elif isinstance(value, np.ndarray):
        _reject_intervals(value.tolist())
    elif isinstance(value, (tuple, list)):
        for item in value:
            _reject_intervals(item)


def _finite_tree(value, name):
    """Check numeric leaves of a provider receipt, keeping text metadata."""
    _reject_intervals(value)
    if isinstance(value, Mapping):
        for key, item in value.items():
            _finite_tree(item, f"{name}.{key}")
    elif isinstance(value, np.ndarray):
        _finite_tree(value.tolist(), name)
    elif isinstance(value, (tuple, list)):
        for item in value:
            _finite_tree(item, name)
    elif isinstance(value, (Number, np.number)) and not np.isfinite(complex(value)):
        raise ValueError(f"{name} requires finite provider values")


def _numeric_array(value, name):
    """Validate a finite numeric array without silently consuming intervals."""
    _reject_intervals(value)
    result = np.asarray(value, complex)
    if not result.size or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} requires finite nonempty numeric data")
    return result


def _scalar(value):
    """Read numbers/rational strings, without discarding interval enclosures."""
    if value is None:
        return None
    _reject_intervals(value)
    if isinstance(value, str) and "/" in value:
        value = Fraction(value)
    if isinstance(value, Mapping):
        if set(value) != {"real", "imag"}:
            raise ValueError("complex scalar needs real and imag components")
        real, imaginary = _scalar(value["real"]), _scalar(value["imag"])
        if real is None or imaginary is None or real.imag != 0 or imaginary.imag != 0:
            raise ValueError("real and imag scalar components must be real finite values")
        value = complex(real.real, imaginary.real)
    result = complex(value)
    if not np.isfinite(result):
        raise ValueError("finite supplied scalar required")
    return result


def _serializable(value):
    if isinstance(value, Mapping):
        return {str(k): _serializable(v) for k, v in value.items()}
    if isinstance(value, np.ndarray):
        return _serializable(value.tolist())
    if isinstance(value, (tuple, list)):
        return [_serializable(v) for v in value]
    if isinstance(value, (complex, np.complexfloating)):
        return float(value.real) if value.imag == 0 else dict(real=float(value.real), imag=float(value.imag))
    if isinstance(value, np.generic):
        return value.item()
    return value


def _owned(packet, identity, name):
    if packet is None:
        return None
    if not identity or packet.get("owner_identity") != identity:
        raise ValueError(f"{name} requires the same explicit owner action/domain/source/branch identity")
    return packet


def _jets(packet, identity, name):
    packet = _owned(packet, identity, name)
    return {k: None if packet is None else _scalar(packet.get(k)) for k in JET_KEYS}


def _stage(value, missing=()):
    return dict(status="UNEVALUATED" if missing else "EVALUATED_SUPPLIED_OWNER_OPERANDS",
                value=value, missing=list(missing))


def _provider(packet, identity, name, context):
    packet = _owned(packet, identity, name)
    if packet is None:
        return None
    # Providers consume the computed cutoff/R_ind/response from this call.
    # Precomputed native response numbers do not bypass this dependency.
    if not callable(packet.get("evaluate")):
        raise ValueError(f"{name} requires a supplied same-owner directional evaluate callable")
    result = packet["evaluate"](context)
    _finite_tree(result, name)
    return result


def completed_photon_column(*, K_primitive, R_ind_action, M, shift, current):
    """Solve one supplied completed native photon column, keeping its Gram.

    The caller must supply the FULL owned forms on the consumed quotient.
    This routine does not build R_ind_action from a single mixed scalar.
    No explicit inverse, eigensolve or angular-primitive substitution occurs.
    """
    K, R, mass = [_numeric_array(x, name) for x, name in
                  ((K_primitive, "K_primitive"), (R_ind_action, "R_ind_action"), (M, "M"))]
    rhs = _numeric_array(current, "current")
    if K.ndim != 2 or K.shape[0] != K.shape[1] or R.shape != K.shape or mass.shape != K.shape:
        raise ValueError("complete co-based square photon forms required")
    if rhs.shape != (K.shape[0],) or not all(np.all(np.isfinite(x)) for x in (K, R, mass, rhs)):
        raise ValueError("one finite current column in the same photon dual required")
    shifted = K + R + _scalar(shift) * mass
    response = _numeric_array(np.linalg.solve(shifted, rhs), "completed photon response")
    residual = _numeric_array(shifted @ response - rhs, "completed photon residual")
    residual_norm = float(np.linalg.norm(residual))
    if not np.isfinite(residual_norm):
        raise ValueError("completed photon residual magnitude must be finite")
    return dict(response=response, residual=residual, residual_norm=residual_norm,
                equation="(K_primitive+R_ind_action+zeta M) u=J",
                scope="SUPPLIED_COMPLETE_QUOTIENT_FORMS__NO_NATIVE_OPERATOR_PRODUCTION")


def make_control_downstream_inputs(owner_identity="FINITE_CONTROL_ACTION_V1"):
    """Prescribed finite chain for replay/tests; never physical BHSM operands.

    The one-dimensional heat action is -E1(c P)/2 with positive
    P=2+v/10+J/5+3vJ/100 near the base.  A supplied photon action then
    consumes its matching remainder.  The two prescribed family actions
    P_e=6/5+u t and P_mu=9/5+u t supply their exact first heat cotangents.
    Fixed control states/domain give the expressly supplied zero ledger
    terms.  The strong entry is a subset and is never summed again.
    """
    def heat(context):
        c = context["cutoff"]["c"]
        p, pv, pj, pvj = 2., .1, .2, .03
        exponential = np.exp(-c*p)
        q = exponential/(2*p)
        q_prime = -exponential*(1+c*p)/(2*p*p)
        return dict(fixed_length_mixed=q*pvj+q_prime*pv*pj,
                    T=exponential, H_P=p*exponential, H_v=pv*exponential, H_J=pj*exponential,
                    classification="PRESCRIBED_FINITE_SCALAR_HEAT_CONTROL")

    def photon(context):
        result = completed_photon_column(K_primitive=[[2]], R_ind_action=[[context["R_ind"]]],
                                         M=[[1.5]], shift="1/3", current=[.25])
        result["classification"] = "PRESCRIBED_FINITE_COMPLETED_PHOTON_CONTROL"
        result["consumed_R_ind"] = context["R_ind"]
        return result

    def paired(context):
        c = context["cutoff"]["c"]
        response = context["native_photon_response"]["response"][0]
        electron = np.exp(-c*1.2)/(2*1.2)*response
        muon = np.exp(-c*1.8)/(2*1.8)*response
        dirac = np.array([1, 0, 0], complex)
        pauli = np.array([2j, 1, 0], complex)
        return dict(electron_vertex=dirac+electron*pauli, muon_vertex=dirac+muon*pauli,
                    ledger={"native_bulk_heat": muon-electron, "state_variation": 0,
                            "contact": 0, "domain_boundary": 0, "completion_counterterm": 0,
                            "strong_within_native": (muon-electron)/4},
                    strong_is_subset=True,
                    classification="PRESCRIBED_FINITE_FAMILY_HEAT_CONTROLS__NO_PHYSICAL_PARTICLE_INPUT")

    def owned(evaluate):
        return dict(owner_identity=owner_identity, evaluate=evaluate)
    return dict(
        ae4_heat=owned(heat), relative_zeta_eta=owned(lambda context: .07),
        local_subtraction=owned(lambda context: .03),
        native_photon_response=owned(photon), paired_native_heat=owned(paired),
        pauli=dict(owner_identity=owner_identity,
                   electron_dirac=[1, 0, 0], electron_pauli=[2j, 1, 0],
                   muon_dirac=[1, 0, 0], muon_pauli=[2j, 1, 0], q_squared=-.2),
    )


def continue_native_kkt_downstream(
    owner_z=None, *, owner_identity=None, surface_jacobi=None, inertia=None, downstream=None,
):
    """Compose z, total branch jets, AE4, photon, paired heat and Pauli.

    Scalar packets contain owner_identity and explicit value/v/J/vJ.  z is
    the owner KKT Schur contraction; its source jets are NOT inferred from
    its value.  surface_jacobi is <psi,gamma J_Sigma psi>, inertia is <psi,I psi>.
    Their jets must already include branch, event, pairing and domain motion.

    downstream slots are owned directional providers ``ae4_heat`` (returning
    fixed_length_mixed,T,H_P,H_v,H_J), ``relative_zeta_eta`` and
    ``local_subtraction`` (returning scalars), ``native_photon_response``
    (returning response and residual), and ``paired_native_heat`` (returning
    electron_vertex,muon_vertex,ledger,strong_is_subset).  ``pauli`` contains
    the owned electron/muon Dirac/Pauli bases and q_squared.  These providers
    supply the native realizations missing from the retained primitives;
    the API does not equate a seven-port kinematic output to an action dual.
    """
    operands = {} if downstream is None else downstream
    # Reject identity mismatches even when an earlier dependency is missing.
    for name, packet in operands.items():
        _owned(packet, owner_identity, name)
    z = _jets(owner_z, owner_identity, "owner_z")
    surface = _jets(surface_jacobi, owner_identity, "surface_jacobi")
    i = _jets(inertia, owner_identity, "inertia")
    r = {k: None if z[k] is None or surface[k] is None else z[k] + surface[k] for k in JET_KEYS}
    stages = {
        "owner_impedance": _stage(z, [f"z_{k}" for k in JET_KEYS if z[k] is None]),
        "total_resistance": _stage(r, [f"r_{k}" for k in JET_KEYS if r[k] is None]),
        "matching_inertia": _stage(i, [f"i_{k}" for k in JET_KEYS if i[k] is None]),
    }
    context = dict(owner_identity=owner_identity, z=z, surface_jacobi=surface, r=r, i=i)
    cutoff = dict(c=None, c_v=None, c_J=None, c_vJ=None)
    if r["value"] is not None and i["value"] is not None:
        base = (surface["value"], z["value"], i["value"])
        if any(x.imag != 0 for x in base):
            raise ValueError("real physical base surface/impedance/inertia contractions required")
        cutoff["c"] = native_heat_length_squared(surface_jacobi=base[0].real,
                                               bulk_impedance=base[1].real, kinetic_inertia=base[2].real)
    missing = [f"{name}_{k}" for name, jets in (("r", r), ("i", i)) for k in JET_KEYS if jets[k] is None]
    coefficients = None
    if not missing:
        def old_keys(jets):
            return dict(value=jets["value"], x=jets["v"], y=jets["J"], xy=jets["vJ"])
        got = cutoff_from_total_contractions(old_keys(r), old_keys(i))
        cutoff.update(c_v=got["c_x"], c_J=got["c_y"], c_vJ=got["c_xy"])
        coefficients = lower_limit_coefficients(
            r=r["value"], i=i["value"], r_x=r["v"], r_y=r["J"], r_xy=r["vJ"],
            i_x=i["v"], i_y=i["J"], i_xy=i["vJ"],
        )
    stages["heat_length_squared"] = _stage(cutoff, missing)
    stages["exact_heat_coefficients"] = _stage(coefficients, missing)
    context.update(cutoff=cutoff, heat_coefficients=coefficients)

    heat = None
    heat_missing = list(missing)
    if not heat_missing:
        packet = _provider(operands.get("ae4_heat"), owner_identity, "ae4_heat", context)
        if packet is None:
            heat_missing = ["same-owner fixed heat mixed contraction and T,H_P,H_v,H_J"]
        else:
            required = ("fixed_length_mixed", "T", "H_P", "H_v", "H_J")
            heat_missing = [k for k in required if packet.get(k) is None]
            if not heat_missing:
                values = {k: _scalar(packet[k]) for k in required}
                length = (coefficients["coefficient_T"] * values["T"]
                          + coefficients["coefficient_H_P"] * values["H_P"]
                          + coefficients["coefficient_H_x"] * values["H_v"]
                          + coefficients["coefficient_H_y"] * values["H_J"])
                heat = dict(fixed_length_mixed=values["fixed_length_mixed"],
                            moving_length_mixed=length, total=values["fixed_length_mixed"] + length)
    stages["AE4_heat"] = _stage(heat, heat_missing)
    context["AE4_heat"] = heat

    relative = local = induced = None
    relative_missing = list(heat_missing)
    if not relative_missing:
        relative = _scalar(_provider(operands.get("relative_zeta_eta"), owner_identity, "relative_zeta_eta", context))
        if relative is None:
            relative_missing = ["same-owner relative-zeta/eta mixed completion"]
    stages["relative_zeta_eta"] = _stage(relative, relative_missing)
    context["relative_zeta_eta"] = relative
    induced_missing = list(relative_missing)
    if not induced_missing:
        local = _scalar(_provider(operands.get("local_subtraction"), owner_identity, "local_subtraction", context))
        if local is None:
            induced_missing = ["same-owner already-owned local mixed subtraction"]
        else:
            induced = heat["total"] + relative - local
    stages["R_ind"] = _stage(induced, induced_missing)
    context.update(R_ind=induced, local_subtraction=local)

    photon = paired = projection = None
    photon_missing = list(induced_missing)
    if not photon_missing:
        photon = _provider(operands.get("native_photon_response"), owner_identity, "native_photon_response", context)
        if photon is None:
            photon_missing = ["completed same-owner photon action on the reached current and response"]
        elif photon.get("response") is None or photon.get("residual") is None:
            raise ValueError("native photon provider must retain response and owned residual")
        else:
            response = _numeric_array(photon["response"], "native photon response")
            residual = _numeric_array(photon["residual"], "native photon residual")
            if response.shape != residual.shape:
                raise ValueError("native photon residual must replay the same response column shape")
            # Preserve the supplied residual as evidence.  Its finite magnitude
            # is not a continuum error enclosure or an exact-zero claim.
    stages["native_photon_response"] = _stage(photon, photon_missing)
    context["native_photon_response"] = photon
    paired_missing = list(photon_missing)
    if not paired_missing:
        paired = _provider(operands.get("paired_native_heat"), owner_identity, "paired_native_heat", context)
        if paired is None:
            paired_missing = ["paired electron-muon native heat, state/contact/domain/completion and matching"]
        else:
            if not paired.get("strong_is_subset"):
                raise ValueError("strong heat must be a subset of native, never an extra addend")
            paired_missing = [k for k in PAIRED_LEDGER if paired.get("ledger", {}).get(k) is None]
            paired_missing += [k for k in ("electron_vertex", "muon_vertex") if paired.get(k) is None]
            for key in PAIRED_LEDGER:
                value = paired.get("ledger", {}).get(key)
                if value is not None:
                    _numeric_array(value, f"paired ledger {key}")
            for key in ("electron_vertex", "muon_vertex"):
                if paired.get(key) is not None:
                    _numeric_array(paired[key], key)
    stages["paired_electron_muon_native_heat"] = _stage(paired, paired_missing)
    pauli_missing = list(paired_missing)
    if not pauli_missing:
        pauli = operands.get("pauli")
        if pauli is None:
            pauli_missing = ["same-owner Pauli tensor bases and controlled signed-transfer readout"]
        else:
            required = ("electron_dirac", "electron_pauli", "muon_dirac", "muon_pauli", "q_squared")
            pauli_missing = [key for key in required if pauli.get(key) is None]
        if not pauli_missing:
            for key in ("electron_dirac", "electron_pauli", "muon_dirac", "muon_pauli"):
                _numeric_array(pauli[key], key)
            q_squared = _scalar(pauli["q_squared"])
            if q_squared.imag != 0:
                raise ValueError("real finite q_squared required")
            projected = {}
            for family in ("electron", "muon"):
                got = project_electromagnetic_form_factors(
                    paired[f"{family}_vertex"], pauli[f"{family}_dirac"], pauli[f"{family}_pauli"],
                    q_squared=q_squared.real,
                )
                projected[family] = vars(got)
            projection = dict(**projected, paired_F2=projected["muon"]["F2"] - projected["electron"]["F2"],
                              scope="SUPPLIED_TENSOR_PROJECTION__PHYSICAL_TRANSFER_LIMIT_NOT_PROMOTED")
    stages["Pauli_readout"] = _stage(projection, pauli_missing)
    return _serializable(dict(
        classification="CONDITIONAL_SAME_OWNER_KKT_DOWNSTREAM_COMPOSITION",
        owner_identity=owner_identity, stages=stages,
        physical_a_mu=None, physical_g_mu=None, physical_promotion=False,
        native_operator_or_source_produced=False,
        exact_error_scope="Supplied binary64 scalar/form composition only; no continuum, tail, physical-input or transfer-limit enclosure.",
    ))
