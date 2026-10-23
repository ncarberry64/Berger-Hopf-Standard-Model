"""Same-owner continuation checks, with independently defined finite actions."""
import json

import numpy as np
import pytest
import sympy as sp
from scipy.special import exp1

from bhsm.interface.muon_native_kkt_downstream import (
    continue_native_kkt_downstream, completed_photon_column, make_control_downstream_inputs,
)


IDENTITY = "FINITE_CONTROL_ACTION_V1"


def packet(value, v=None, J=None, vJ=None, identity=IDENTITY):
    return dict(owner_identity=identity, value=value, v=v, J=J, vJ=vJ)


def supplied_controls():
    # Prescribed finite contractions: both surface and KKT terms contribute
    # nonzero first/mixed jets.  These do not stand for physical source data.
    return dict(owner_z=packet("3/2", "1/7", "2/9", "1/11"),
                surface_jacobi=packet("5/4", "2/13", "-1/17", "3/19"),
                inertia=packet("7/3", "2/5", "-3/8", "5/12"))


def polynomials():
    v, j = sp.symbols("v J", real=True)
    z = sp.Rational(3, 2)+v/7+2*j/9+v*j/11
    surface = sp.Rational(5, 4)+2*v/13-j/17+3*v*j/19
    inertia = sp.Rational(7, 3)+2*v/5-3*j/8+5*v*j/12
    return v, j, z+surface, inertia


def test_unknown_owner_source_retains_all_downstream_unevaluated():
    result = continue_native_kkt_downstream()
    assert all(stage["status"] == "UNEVALUATED" for stage in result["stages"].values())
    assert result["stages"]["owner_impedance"]["value"] == dict.fromkeys(("value", "v", "J", "vJ"))
    assert result["physical_a_mu"] is None and result["physical_g_mu"] is None
    assert not result["physical_promotion"] and not result["native_operator_or_source_produced"]
    json.dumps(result, allow_nan=False)


def test_evaluated_z_value_does_not_supply_missing_jets():
    result = continue_native_kkt_downstream(
        packet(1.5), owner_identity=IDENTITY, surface_jacobi=packet(1.25), inertia=packet(7/3),
        downstream=make_control_downstream_inputs(),
    )
    stages = result["stages"]
    assert stages["heat_length_squared"]["value"]["c"] == pytest.approx((7/3)/2.75)
    assert stages["heat_length_squared"]["value"]["c_vJ"] is None
    assert "r_vJ" in stages["heat_length_squared"]["missing"]
    assert "i_vJ" in stages["heat_length_squared"]["missing"]
    assert stages["exact_heat_coefficients"]["value"] is None
    assert stages["Pauli_readout"]["status"] == "UNEVALUATED"


def test_total_resistance_cutoff_and_exact_log_coefficient_against_symbolic_action():
    result = continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY)
    stages = result["stages"]
    v, j, r, i = polynomials()
    zero = {v: 0, j: 0}
    cutoff = stages["heat_length_squared"]["value"]
    for name, expr in (("c", i/r), ("c_v", sp.diff(i/r, v)),
                       ("c_J", sp.diff(i/r, j)), ("c_vJ", sp.diff(i/r, v, j))):
        assert cutoff[name] == pytest.approx(float(expr.subs(zero)), abs=2e-16)
    exact = sp.diff(sp.log(i)-sp.log(r), v, j)/2
    assert stages["exact_heat_coefficients"]["value"]["coefficient_T"] == pytest.approx(float(exact.subs(zero)), abs=2e-16)
    assert stages["total_resistance"]["value"]["vJ"] == pytest.approx(1/11+3/19)
    assert stages["total_resistance"]["value"]["value"] == pytest.approx(2.75)
    assert stages["AE4_heat"]["status"] == "UNEVALUATED"


def test_finite_full_chain_consumes_length_induced_action_response_and_family_heat():
    result = continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY,
                                          downstream=make_control_downstream_inputs())
    stages = result["stages"]
    assert all(stage["status"] == "EVALUATED_SUPPLIED_OWNER_OPERANDS" for stage in stages.values())
    heat = stages["AE4_heat"]["value"]
    c = stages["heat_length_squared"]["value"]["c"]
    # Independent finite differences of the integrated E1 action with BOTH
    # changing P and changing c; this is not a re-evaluation of its formulas.
    v, j, r, inertia = polynomials()
    cutoff = sp.lambdify((v, j), inertia/r, "numpy")
    def action(x, y):
        return -exp1(cutoff(x, y)*(2+.1*x+.2*y+.03*x*y))/2
    h = 1e-4
    mixed = (action(h, h)-action(h, -h)-action(-h, h)+action(-h, -h))/(4*h*h)
    assert heat["total"] == pytest.approx(mixed, abs=2e-9)
    induced = stages["R_ind"]["value"]
    assert induced == pytest.approx(heat["total"]+.07-.03)
    photon = stages["native_photon_response"]["value"]
    assert photon["consumed_R_ind"] == pytest.approx(induced)
    assert photon["response"][0] == pytest.approx(.25/(2+induced+.5))
    assert photon["residual_norm"] < 1e-15
    expected = (np.exp(-c*1.8)/(2*1.8)-np.exp(-c*1.2)/(2*1.2))*photon["response"][0]
    projection = stages["Pauli_readout"]["value"]
    assert projection["paired_F2"] == pytest.approx(expected, abs=1e-16)
    ledger = stages["paired_electron_muon_native_heat"]["value"]["ledger"]
    assert projection["paired_F2"] == pytest.approx(ledger["native_bulk_heat"])
    assert projection["paired_F2"] != pytest.approx(ledger["native_bulk_heat"]+ledger["strong_within_native"])
    assert result["physical_a_mu"] is None and result["physical_promotion"] is False
    json.dumps(result, allow_nan=False)


def test_owner_identity_mismatch_rejected_even_before_missing_dependency():
    with pytest.raises(ValueError, match="same explicit owner"):
        continue_native_kkt_downstream(packet(1, identity="different"), owner_identity=IDENTITY)
    bad = make_control_downstream_inputs()
    bad["paired_native_heat"]["owner_identity"] = "different-source"
    with pytest.raises(ValueError, match="same explicit owner"):
        continue_native_kkt_downstream(owner_identity=IDENTITY, downstream=bad)


def test_partial_paired_ledger_cannot_bypass_missing_native_domain_term():
    providers = make_control_downstream_inputs()
    original = providers["paired_native_heat"]["evaluate"]
    def partial(context):
        got = original(context)
        got["ledger"]["domain_boundary"] = None
        return got
    providers["paired_native_heat"]["evaluate"] = partial
    result = continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY, downstream=providers)
    assert result["stages"]["paired_electron_muon_native_heat"]["missing"] == ["domain_boundary"]
    assert result["stages"]["Pauli_readout"]["value"] is None


def test_complex_current_extension_is_linear_without_current_conjugation():
    supplied = supplied_controls()
    for term in supplied.values():
        term["J"] = complex(sp.Rational(term["J"]))*(2+3j)
        term["vJ"] = complex(sp.Rational(term["vJ"]))*(2+3j)
    got = continue_native_kkt_downstream(**supplied, owner_identity=IDENTITY)
    real = continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY)
    for key in ("c_J", "c_vJ"):
        value = got["stages"]["heat_length_squared"]["value"][key]
        assert complex(value["real"], value["imag"]) == pytest.approx((2+3j)*real["stages"]["heat_length_squared"]["value"][key])


def test_photon_response_replays_completed_action_with_nontrivial_gram():
    primitive = np.array([[3, .2j], [-.2j, 2]], complex)
    induced = np.array([[.3, .1], [.1, .4]])
    mass = np.array([[2, .3], [.3, 1]])
    current = np.array([1j, 2])
    got = completed_photon_column(K_primitive=primitive, R_ind_action=induced,
                                 M=mass, shift=.7, current=current)
    assert np.linalg.norm((primitive+induced+.7*mass)@got["response"]-current) < 1e-15
    assert got["residual_norm"] < 1e-15


@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_nonfinite_scalar_inputs_fail_closed(bad):
    with pytest.raises(ValueError, match="finite supplied"):
        continue_native_kkt_downstream(packet(bad), owner_identity=IDENTITY)


@pytest.mark.parametrize("name", ["K_primitive", "R_ind_action", "M", "current"])
def test_photon_column_rejects_nested_interval_entries_before_conversion(name):
    from flint import arb
    supplied = dict(K_primitive=[[2]], R_ind_action=[[.3]], M=[[1.5]], shift=.2, current=[.25])
    supplied[name] = np.array([arb(1, .1)], dtype=object) if name == "current" else [[arb(1, .1)]]
    with pytest.raises(TypeError, match="interval downstream backend"):
        completed_photon_column(**supplied)


@pytest.mark.parametrize("component", ["real", "imag"])
def test_complex_mapping_interval_components_are_not_coerced_to_midpoints(component):
    from flint import arb
    value = dict(real=1., imag=0.)
    value[component] = arb(1, .1)
    with pytest.raises(TypeError, match="interval downstream backend"):
        continue_native_kkt_downstream(packet(value), owner_identity=IDENTITY)


@pytest.mark.parametrize("field", ["response", "residual", "residual_norm"])
@pytest.mark.parametrize("bad", [float("nan"), float("inf")])
def test_nonfinite_photon_provider_values_cannot_reach_paired_heat(field, bad):
    providers = make_control_downstream_inputs()
    original = providers["native_photon_response"]["evaluate"]
    def invalid(context):
        result = original(context)
        result[field] = bad if field == "residual_norm" else [bad]
        return result
    providers["native_photon_response"]["evaluate"] = invalid
    with pytest.raises(ValueError, match="finite provider"):
        continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY, downstream=providers)


@pytest.mark.parametrize("slot,field", [("native_photon_response", "response"),
                                       ("native_photon_response", "residual"),
                                       ("paired_native_heat", "electron_vertex"),
                                       ("paired_native_heat", "muon_vertex"),
                                       ("paired_native_heat", "ledger")])
def test_nested_provider_intervals_are_rejected_before_continuation(slot, field):
    from flint import arb
    providers = make_control_downstream_inputs()
    original = providers[slot]["evaluate"]
    def invalid(context):
        result = original(context)
        if field == "ledger":
            result[field]["domain_boundary"] = np.array([arb(1, .1)], dtype=object)
        else:
            result[field] = np.array([arb(1, .1)], dtype=object)
        return result
    providers[slot]["evaluate"] = invalid
    with pytest.raises(TypeError, match="interval downstream backend"):
        continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY, downstream=providers)


@pytest.mark.parametrize("field", ["electron_vertex", "muon_vertex", "ledger"])
def test_nonfinite_paired_vertices_and_ledger_are_rejected(field):
    providers = make_control_downstream_inputs()
    original = providers["paired_native_heat"]["evaluate"]
    def invalid(context):
        result = original(context)
        if field == "ledger":
            result[field]["contact"] = float("nan")
        else:
            result[field] = [1, float("nan"), 0]
        return result
    providers["paired_native_heat"]["evaluate"] = invalid
    with pytest.raises(ValueError, match="finite provider"):
        continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY, downstream=providers)


@pytest.mark.parametrize("missing", ["electron_dirac", "electron_pauli", "muon_dirac", "muon_pauli", "q_squared"])
def test_incomplete_pauli_packet_reports_exact_unevaluated_field(missing):
    providers = make_control_downstream_inputs()
    del providers["pauli"][missing]
    result = continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY, downstream=providers)
    assert result["stages"]["paired_electron_muon_native_heat"]["status"] == "EVALUATED_SUPPLIED_OWNER_OPERANDS"
    assert result["stages"]["Pauli_readout"] == dict(status="UNEVALUATED", value=None, missing=[missing])
    json.dumps(result, allow_nan=False)


def test_finite_nonzero_provider_residual_is_retained_without_error_bound_claim():
    providers = make_control_downstream_inputs()
    original = providers["native_photon_response"]["evaluate"]
    def inexact(context):
        result = original(context)
        result["residual"] = [.125]
        result["residual_norm"] = .125
        return result
    providers["native_photon_response"]["evaluate"] = inexact
    result = continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY, downstream=providers)
    assert result["stages"]["native_photon_response"]["value"]["residual"] == [.125]
    assert result["stages"]["native_photon_response"]["value"]["residual_norm"] == .125
    assert result["physical_promotion"] is False


def test_pauli_basis_interval_is_rejected_before_projection():
    from flint import arb
    providers = make_control_downstream_inputs()
    providers["pauli"]["muon_pauli"] = [arb(1, .1), 1, 0]
    with pytest.raises(TypeError, match="interval downstream backend"):
        continue_native_kkt_downstream(**supplied_controls(), owner_identity=IDENTITY, downstream=providers)
