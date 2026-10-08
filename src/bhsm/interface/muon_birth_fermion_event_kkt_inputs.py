"""Physical input receipt for the retained fermion-family E1 jet callback.

No new event assembly is implemented here. The six triples are the existing
callback arguments. Missing physical values stay None and stop its invocation.
The exact quadratic identities below are independent mathematical checks.
"""
from __future__ import annotations

import inspect
import json
from hashlib import sha256
from pathlib import Path

import sympy as sp

from bhsm.interface.ae4_event_response_jet_integration import (
    canonical_noether_flux_balance_jet,
    solve_retarded_event_kkt_jet,
)


ARGUMENT_OPERANDS = (
    ("parent_jet", "P_F"),
    ("coupling_jet", "B_F"),
    ("child_retarded_jet", "L_F"),
    ("response_jet", "C_F"),
    ("source_jet", "J_F"),
    ("response_target_jet", "d_F"),
)
ARTIFACT_DIRECTORY = "artifacts/muon_birth_fermion_event_kkt_inputs_20261008"
STARTING_HEAD = "86a602c8c4b357d6e13dd4409ee5e2f1bcb37e1c"


def _exact_matrix(value, name, *, vector=False):
    if value is None:
        raise ValueError(name + " is absent")
    result = sp.ImmutableMatrix(value)
    if result.rows == 0 or (not vector and result.rows != result.cols):
        raise ValueError(name + " must be nonempty and square")
    if vector and result.cols != 1:
        raise ValueError(name + " must be a column vector")
    for entry in result:
        real, imaginary = sp.expand(entry).as_real_imag()
        if real.is_Rational is not True or imaginary.is_Rational is not True:
            raise ValueError(name + " requires exact rational real/imaginary entries")
    return result


def _zero(value):
    return all(sp.expand(entry) == 0 for entry in value)


def quadratic_noether_real_kernel(operator, generator):
    """Return H-dagger T-T H, including a possibly non-Hermitian retarded H.

    For T-dagger=-T this kernel is Hermitian and represents exactly
    2 Re <Tq,Hq>. It includes no explicit-source or multiplier term.
    """
    h = _exact_matrix(operator, "operator")
    t = _exact_matrix(generator, "generator")
    if h.shape != t.shape:
        raise ValueError("operator and generator dimensions must agree")
    if not _zero(t.adjoint()+t):
        raise ValueError("generator must be anti-Hermitian")
    kernel = sp.ImmutableMatrix(h.adjoint()*t-t*h)
    if not _zero(kernel-kernel.adjoint()):
        raise ValueError("quadratic real kernel must be Hermitian")
    return kernel


def quadratic_noether_commutator_kernel(operator, generator):
    """Return [H,T] only for a verified Hermitian quadratic operator H."""
    h = _exact_matrix(operator, "operator")
    if not _zero(h-h.adjoint()):
        raise ValueError("commutator identity requires a Hermitian operator")
    return quadratic_noether_real_kernel(h, generator)


def verify_quadratic_noether_identity(operator, generator, trace):
    """Verify the requested commutator identity on exact SUPPLIED inputs.

    This selects no physical E1 operator, trace or state. Non-Hermitian
    retarded operators require quadratic_noether_real_kernel instead.
    """
    h = _exact_matrix(operator, "operator")
    t = _exact_matrix(generator, "generator")
    q = _exact_matrix(trace, "trace", vector=True)
    if q.rows != h.rows:
        raise ValueError("trace and operator dimensions must agree")
    kernel = quadratic_noether_commutator_kernel(h, t)
    value = ((t*q).adjoint()*h*q)[0]
    lhs = sp.expand(value+sp.conjugate(value))
    rhs = sp.expand((q.adjoint()*kernel*q)[0])
    return dict(lhs=lhs, rhs=rhs, residual=sp.expand(lhs-rhs),
                physical_E1_kernel_evaluated=False,
                scope="EXACT_SUPPLIED_HERMITIAN_QUADRATIC_IDENTITY",
                explicit_source_included=False)


def symbolic_quadratic_identity():
    """Universal polarized identity, independent of finite numerical probes."""
    h, ht, t, td, q, qd = sp.symbols(
        "H H_dagger T T_dagger q q_dagger", commutative=False)
    # The conjugate scalar is q-dagger H-dagger T q.
    lhs = qd*td*h*q+qd*ht*t*q
    general = sp.expand(lhs.subs(td, -t))
    expected = qd*(ht*t-t*h)*q
    general_residual = sp.expand(general-expected)
    hermitian = sp.expand(general.subs(ht, h))
    commutator = qd*(h*t-t*h)*q
    hermitian_residual = sp.expand(hermitian-commutator)
    if general_residual != 0 or hermitian_residual != 0:
        raise ValueError("Quadratic identity derivation failed")
    return dict(
        general_kernel="H_eff^dagger T-T H_eff",
        general_residual=str(general_residual),
        Hermitian_kernel="[H_eff,T]=H_eff T-T H_eff",
        Hermitian_residual=str(hermitian_residual),
        Hermitian_condition_required=True,
        retarded_Hermitianity_not_assumed=True,
        occupation_convention="N=I-C_plus; delta B=-Tr(delta C_plus K)",
        source_term="2 Re <Tq,J>=-q^dagger T J+J^dagger Tq (linear in q at fixed J)",
        source_forced_into_quadratic_commutator=False,
        physical_E1_kernel_evaluated=False,
    )


def first_unavailable(solver_inputs):
    """Name the first absent existing argument and derivative order."""
    if tuple(inspect.signature(solve_retarded_event_kkt_jet).parameters) != tuple(
            argument for argument, _ in ARGUMENT_OPERANDS):
        raise ValueError("Retained six-argument callback contract changed")
    for argument, operand in ARGUMENT_OPERANDS:
        values = solver_inputs[argument]
        if len(values) != 3:
            raise ValueError(argument + " requires three derivative orders")
        for order, value in enumerate(values):
            if value is None:
                return dict(argument=argument, operand=operand,
                            derivative_order=order, tuple_index=order)
    return None


def physical_input_packet(root):
    """Read audited physical values; no absent argument gets a zero default."""
    root = Path(root)
    receipt = json.loads((root / ARTIFACT_DIRECTORY / "physical_input_inventory.json").read_text(encoding="utf8"))
    if receipt["starting_head"] != STARTING_HEAD or receipt["sector"] != "fermion_family":
        raise ValueError("Physical input receipt has the wrong action/head/sector binding")
    if (receipt["incoming"] != dict(branch=23, event="E1_minus", source_state_slice=[98, 196])
            or receipt["outgoing"] != dict(branch=24, event="E1_plus", source_state_slice=[0, 98])
            or receipt["same_common_event"] is not True):
        raise ValueError("Physical input receipt must bind the same E1 incoming/outgoing domain")
    def verify(item):
        if isinstance(item, dict):
            path = item.get("path", item.get("source_path"))
            digest = item.get("raw_sha256", item.get("sha256"))
            if path and digest:
                raw = (root / path).read_bytes()
                accepted = {sha256(raw).hexdigest()}
                if Path(path).suffix in {".py", ".json", ".md", ".txt"}:
                    accepted.add(sha256(raw.replace(b"\r\n", b"\n")).hexdigest())
                if digest.lower() not in accepted:
                    raise ValueError("Physical input source identity changed: " + path)
            for child in item.values():
                verify(child)
        elif isinstance(item, list):
            for child in item:
                verify(child)
    verify(receipt)
    parent_receipt = json.loads((root / ARTIFACT_DIRECTORY / "parent_operand_receipt.json").read_text(encoding="utf8"))
    if receipt["parent_operand_receipt"] != parent_receipt:
        raise ValueError("Embedded parent receipt disagrees with the audited source")
    inputs = {argument: receipt["solver_inputs"][argument]
              for argument, _ in ARGUMENT_OPERANDS}
    rows = receipt["input_rows"]
    if [(row["argument"], row["operand"]) for row in rows] != list(ARGUMENT_OPERANDS):
        raise ValueError("Physical input rows disagree with the retained callback arguments")
    for row in rows:
        entries = row["entries"]
        if [entry["derivative_order"] for entry in entries] != [0, 1, 2]:
            raise ValueError("Physical input rows require derivative orders 0, 1, 2")
        if inputs[row["argument"]] != [entry["value"] for entry in entries]:
            raise ValueError("Physical input values disagree with the audited rows")
    missing = first_unavailable(inputs)
    declared = receipt["parent_operand_receipt"]["first_unavailable"]
    if ((missing is None) != (declared is None)
            or missing is not None and any(missing[key] != declared[key]
                                          for key in ("argument", "operand", "derivative_order"))):
        raise ValueError("Audited first operand disagrees with the materialized tuple values")
    return dict(
        starting_head=STARTING_HEAD,
        classification="EXISTING_FERMION_FAMILY_E1_JET_INPUT_INSTANTIATION_ATTEMPT",
        domain="incoming_C1_branch23_E1_minus__outgoing_C2_branch24_E1_plus",
        solver="bhsm.interface.ae4_event_response_jet_integration.solve_retarded_event_kkt_jet",
        noether="bhsm.interface.ae4_event_response_jet_integration.canonical_noether_flux_balance_jet",
        solver_inputs=inputs,
        physical_generator=receipt.get("physical_generator"),
        derivative_orders=[0, 1, 2], derivatives_are_Taylor_coefficients=False,
        physical_input_inventory=receipt,
        first_unavailable=missing,
        quadratic_identity=symbolic_quadratic_identity(),
        solver_invoked=False, noether_invoked=False,
        effective_retarded_parent_jet=None, event_traction_jets=None,
        physical_quadratic_covariance_kernel=None,
        complete_projected_CAR_kernel=None, minimal_moment_span=None,
        selected_covariance=None, state_independence=None,
        claims=dict(
            DERIVED="Exact Hermitian commutator and general retarded real quadratic identities; explicit-source scope and six-argument input contract",
            EVALUATED="Bounded physical input inventory, source/packet identities and exact symbolic identity",
            CONTROL_ONLY="Synthetic exact inputs in focused algebra tests; no physical solver substituted",
            UNEVALUATED="Physical inputs without numerical provenance; retained solve/Noether/CAR projection cannot run before the first unavailable input is supplied",
            OWNER_DEFINITION_GAP="No new assembly or owner definition requested",
        ),
    )


def call_retained_solver_and_noether(solver_inputs, generator):
    """Direct handoff only; the retained implementation does all assembly.

    This guard reports the actual unavailable tuple entry before numpy can
    coerce None to a nonfinite value. It adds no KKT equation or defaults.
    If only the Noether generator is absent, retain the actual solver result.
    """
    missing = first_unavailable(solver_inputs)
    if missing is not None:
        raise ValueError("Unavailable physical operand: " + missing["operand"]
                         + " derivative order " + str(missing["derivative_order"])
                         + " (" + missing["argument"] + "["
                         + str(missing["tuple_index"]) + "])")
    response = solve_retarded_event_kkt_jet(**solver_inputs)
    if generator is None:
        # Preserve an actual solve if only the separate Noether input is absent.
        return response, None
    noether = canonical_noether_flux_balance_jet(
        trace_jet=response["parent_trace_jet"],
        event_traction_jets=response["event_traction_jets"],
        generator=generator,
    )
    return response, noether
