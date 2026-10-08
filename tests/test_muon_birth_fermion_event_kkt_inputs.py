"""CONTROL_ONLY exact identities and input guards, with no KKT solve.

Symbolic matrices below prove algebraic laws on supplied normalized finite
coordinates. They are not the retained E1 fermion operator, state, source,
or a physical birth verdict.
"""
from functools import wraps
import json
from pathlib import Path
import shutil

import pytest
import sympy as sp

from bhsm.interface.muon_birth_fermion_event_kkt_inputs import (
    ARGUMENT_OPERANDS,
    ARTIFACT_DIRECTORY,
    call_retained_solver_and_noether,
    first_unavailable,
    physical_input_packet,
    quadratic_noether_commutator_kernel,
    quadratic_noether_real_kernel,
    verify_quadratic_noether_identity,
)
from bhsm.interface.muon_birth_covariance_sensitivity import occupation_sensitivity_kernel


ROOT = Path(__file__).resolve().parents[1]


def scalar(matrix):
    assert matrix.shape == (1, 1)
    return sp.expand(matrix[0, 0])


def test_universal_symbolic_noether_commutator_identity_has_correct_sign():
    """Independent general complex 2D proof, not one chosen numerical q."""
    h1, h2, hx, hy, ta, tb, tx, ty = sp.symbols(
        "h1 h2 hx hy ta tb tx ty", real=True)
    q1r, q1i, q2r, q2i = sp.symbols("q1r q1i q2r q2i", real=True)
    h = sp.Matrix([[h1, hx+sp.I*hy], [hx-sp.I*hy, h2]])
    t = sp.Matrix([[sp.I*ta, tx+sp.I*ty], [-tx+sp.I*ty, sp.I*tb]])
    q = sp.Matrix([q1r+sp.I*q1i, q2r+sp.I*q2i])
    assert h == h.adjoint()
    assert t.adjoint() == -t
    lhs = sp.expand(2*sp.re(scalar((t*q).adjoint()*h*q)))
    rhs = scalar(q.adjoint()*(h*t-t*h)*q)
    assert sp.expand(lhs-rhs) == 0
    assert sp.expand(lhs+rhs) != 0
    assert all(sp.expand(entry) == 0 for entry in (h*t-t*h).adjoint()-(h*t-t*h))


def test_supplied_exact_api_commutator_is_h_t_minus_t_h():
    h = sp.diag(1, 3)
    t = sp.Matrix([[0, 1], [-1, 0]])
    q = sp.Matrix([1, 1])
    kernel = quadratic_noether_commutator_kernel(h, t)
    assert kernel == sp.Matrix([[0, -2], [-2, 0]])
    result = verify_quadratic_noether_identity(h, t, q)
    assert result["lhs"] == result["rhs"] == -4
    assert result["residual"] == 0
    assert result["physical_E1_kernel_evaluated"] is False


def test_complex_exact_inputs_preserve_real_quadratic_identity():
    h = sp.Matrix([[2, 1+sp.I], [1-sp.I, 4]])
    t = sp.Matrix([[sp.I, 2+sp.I], [-2+sp.I, -3*sp.I]])
    q = sp.Matrix([sp.Rational(2, 3)+sp.I/5, -sp.Rational(3, 7)+2*sp.I])
    kernel = quadratic_noether_commutator_kernel(h, t)
    assert all(sp.expand(entry) == 0 for entry in kernel-kernel.adjoint())
    independently_derived = scalar(q.adjoint()*(h*t-t*h)*q)
    result = verify_quadratic_noether_identity(h, t, q)
    assert sp.expand(result["lhs"]-independently_derived) == 0
    assert sp.expand(result["rhs"]-independently_derived) == 0
    assert result["residual"] == 0


def test_ordered_covariance_response_has_negative_commutator_kernel():
    h = sp.diag(1, 3)
    t = sp.Matrix([[0, 1], [-1, 0]])
    kernel = quadratic_noether_commutator_kernel(h, t)
    c1 = sp.Matrix([[sp.Rational(1, 2), sp.Rational(1, 7)],
                    [sp.Rational(1, 7), sp.Rational(1, 3)]])
    x = sp.Matrix([[sp.Rational(1, 9), sp.Rational(1, 11)+sp.I/13],
                   [sp.Rational(1, 11)-sp.I/13, -sp.Rational(1, 17)]])
    c2 = c1+x
    n1, n2 = sp.eye(2)-c1, sp.eye(2)-c2
    # This is a finite ordered STATE DIFFERENCE, without a Wick subtraction.
    difference = sp.expand(sp.trace(kernel*n2)-sp.trace(kernel*n1))
    expected = sp.expand(-sp.trace(kernel*x))
    assert difference == expected != 0
    assert occupation_sensitivity_kernel(kernel) == -kernel
    assert sp.expand(sp.trace(occupation_sensitivity_kernel(kernel)*x)) == expected


def test_explicit_j_source_is_linear_and_cannot_be_forced_into_commutator():
    t = sp.Matrix([[0, 1], [-1, 0]])
    q = sp.Matrix([1, 0])
    source = sp.Matrix([0, 1])
    h = sp.zeros(2)
    value = sp.expand(2*sp.re(scalar((t*q).adjoint()*source)))
    explicit_formula = scalar(-q.adjoint()*t*source+source.adjoint()*t*q)
    assert value == explicit_formula == -2
    assert sp.expand(2*sp.re(scalar((t*(-q)).adjoint()*source))) == -value
    quadratic = quadratic_noether_commutator_kernel(h, t)
    assert scalar(q.adjoint()*quadratic*q) == 0
    # Every q-dagger K q is even under q -> -q; the explicit source is odd.
    a, b, c, d = sp.symbols("a b c d", real=True)
    arbitrary_kernel = sp.Matrix([[a, b+sp.I*c], [b-sp.I*c, d]])
    assert scalar((-q).adjoint()*arbitrary_kernel*(-q)) == scalar(q.adjoint()*arbitrary_kernel*q)


def test_nonhermitian_retarded_block_requires_general_kernel_not_commutator():
    h = sp.Matrix([[1+sp.I, 2], [0, 3+2*sp.I]])
    t = sp.Matrix([[0, 1], [-1, 0]])
    q = sp.Matrix([1, sp.I])
    exact_real_kernel = h.adjoint()*t-t*h
    lhs = sp.expand(2*sp.re(scalar((t*q).adjoint()*h*q)))
    assert sp.expand(lhs-scalar(q.adjoint()*exact_real_kernel*q)) == 0
    api_kernel = quadratic_noether_real_kernel(h, t)
    assert all(sp.expand(entry) == 0 for entry in api_kernel-exact_real_kernel)
    assert all(sp.expand(entry) == 0 for entry in api_kernel-api_kernel.adjoint())
    assert sp.expand(lhs-scalar(q.adjoint()*(h*t-t*h)*q)) != 0
    with pytest.raises(ValueError):
        quadratic_noether_commutator_kernel(h, t)
    with pytest.raises(ValueError):
        verify_quadratic_noether_identity(h, t, q)


@pytest.mark.parametrize("h,t", [
    (sp.Matrix([[1, 1], [0, 2]]), sp.Matrix([[0, 1], [-1, 0]])),
    (sp.eye(2), sp.Matrix([[0, 1], [1, 0]])),
    (sp.eye(2), sp.eye(3)),
    (sp.Matrix([[sp.Rational(1, 2), 0]]), sp.eye(2)),
    (None, sp.eye(2)),
])
def test_invalid_operator_symmetry_dimensions_or_absence_are_rejected(h, t):
    with pytest.raises(ValueError):
        quadratic_noether_commutator_kernel(h, t)


def test_commuting_quadratic_piece_zero_does_not_erase_source_piece():
    h = 2*sp.eye(2)
    t = sp.Matrix([[0, 1], [-1, 0]])
    assert quadratic_noether_commutator_kernel(h, t) == sp.zeros(2)
    source_piece = 2*sp.re(scalar((t*sp.Matrix([1, 0])).adjoint()*sp.Matrix([0, 1])))
    assert source_piece == -2


def test_missing_operand_guard_prevents_any_retained_solver_invocation(monkeypatch):
    """CONTROL_ONLY guard input: None never becomes an invented zero matrix."""
    import bhsm.interface.muon_birth_fermion_event_kkt_inputs as module
    inputs = {argument: (None, None, None) for argument, _ in ARGUMENT_OPERANDS}

    @wraps(module.solve_retarded_event_kkt_jet)
    def forbidden_call(**kwargs):
        raise AssertionError("missing inputs must stop before the retained solver")

    monkeypatch.setattr(module, "solve_retarded_event_kkt_jet", forbidden_call)
    # wraps preserves the callback signature checked by first_unavailable.
    with pytest.raises(ValueError, match=r"P_F derivative order 0 \(parent_jet\[0\]\)"):
        call_retained_solver_and_noether(inputs, sp.eye(1))


def test_missing_input_order_tracks_existing_argument_then_derivative_order():
    """CONTROL_ONLY presence sentinels; they are not numerically solved."""
    inputs = {argument: ("supplied", "supplied", "supplied")
              for argument, _ in ARGUMENT_OPERANDS}
    inputs["parent_jet"] = ("supplied", None, "supplied")
    inputs["coupling_jet"] = (None, None, None)
    assert first_unavailable(inputs) == {
        "argument": "parent_jet", "operand": "P_F", "derivative_order": 1,
        "tuple_index": 1,
    }
    inputs["parent_jet"] = ("supplied", "supplied", "supplied")
    assert first_unavailable(inputs) == {
        "argument": "coupling_jet", "operand": "B_F", "derivative_order": 0,
        "tuple_index": 0,
    }
    inputs["parent_jet"] = (None, None)
    with pytest.raises(ValueError, match="three derivative orders"):
        first_unavailable(inputs)


@pytest.fixture
def isolated_physical_receipt(tmp_path):
    """Copy audited inputs for tamper tests; never modify retained files."""
    receipt_path = ROOT/ARTIFACT_DIRECTORY/"physical_input_inventory.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf8"))
    paths = set()

    def collect(value):
        if isinstance(value, dict):
            path = value.get("path", value.get("source_path"))
            digest = value.get("raw_sha256", value.get("sha256"))
            if path and digest:
                assert not Path(path).is_absolute()
                paths.add(path)
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    collect(receipt)
    for path in paths:
        destination = tmp_path/path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/path, destination)
    target = tmp_path/ARTIFACT_DIRECTORY/"physical_input_inventory.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt), encoding="utf8")
    return tmp_path, target, receipt


def test_actual_receipt_first_operand_and_all_downstream_values_remain_unavailable():
    packet = physical_input_packet(ROOT)
    assert packet["first_unavailable"] == {
        "argument": "parent_jet", "operand": "P_F", "derivative_order": 0,
        "tuple_index": 0,
    }
    assert all(values == [None, None, None] for values in packet["solver_inputs"].values())
    assert packet["solver_invoked"] is packet["noether_invoked"] is False
    for name in ("effective_retarded_parent_jet", "event_traction_jets",
                 "physical_quadratic_covariance_kernel", "complete_projected_CAR_kernel",
                 "minimal_moment_span", "selected_covariance", "state_independence"):
        assert packet[name] is None
    packet["solver_inputs"]["parent_jet"][0] = "caller mutation"
    assert physical_input_packet(ROOT)["solver_inputs"]["parent_jet"][0] is None


def test_physical_packet_rejects_referenced_source_tampering(isolated_physical_receipt):
    root, _, _ = isolated_physical_receipt
    source = root/"src/bhsm/interface/ae4_event_response_jet_integration.py"
    source.write_bytes(source.read_bytes()+b"\n# receipt tamper test\n")
    with pytest.raises(ValueError, match="source identity changed"):
        physical_input_packet(root)


@pytest.mark.parametrize("side,field,value", [
    ("incoming", "event", "STEP1222"),
    ("outgoing", "event", "E1_minus"),
    ("incoming", "source_state_slice", [0, 98]),
    ("outgoing", "source_state_slice", [98, 196]),
    (None, "same_common_event", False),
])
def test_physical_packet_rejects_event_side_or_state_slice_mismatch(
    isolated_physical_receipt, side, field, value
):
    root, path, receipt = isolated_physical_receipt
    target = receipt if side is None else receipt[side]
    target[field] = value
    path.write_text(json.dumps(receipt), encoding="utf8")
    with pytest.raises(ValueError):
        physical_input_packet(root)


@pytest.mark.parametrize("mutation", ["head", "branches", "declared_operand"])
def test_physical_packet_rejects_audited_binding_mismatches(isolated_physical_receipt, mutation):
    root, path, receipt = isolated_physical_receipt
    if mutation == "head":
        receipt["starting_head"] = "0"*40
    elif mutation == "branches":
        receipt["incoming"]["branch"], receipt["outgoing"]["branch"] = 24, 23
    else:
        receipt["parent_operand_receipt"]["first_unavailable"]["operand"] = "B_F"
    path.write_text(json.dumps(receipt), encoding="utf8")
    with pytest.raises(ValueError):
        physical_input_packet(root)


def test_physical_packet_rejects_zero_fill_contradicting_audited_null_entries(isolated_physical_receipt):
    """CONTROL_ONLY tamper values, never supplied to a numerical callback."""
    root, path, receipt = isolated_physical_receipt
    assert all(row["entries"][0]["value"] is None for row in receipt["input_rows"])
    receipt["solver_inputs"] = {argument: [0, 0, 0] for argument, _ in ARGUMENT_OPERANDS}
    path.write_text(json.dumps(receipt), encoding="utf8")
    with pytest.raises(ValueError):
        physical_input_packet(root)


def test_physical_packet_binds_embedded_parent_receipt_to_its_hash_checked_file(isolated_physical_receipt):
    root, path, receipt = isolated_physical_receipt
    # Retain the original referenced file/digest while changing the embedded
    # audit's event. Hash validation must bind the audit actually consumed.
    receipt["parent_operand_receipt"]["common_event"] = "unrelated_STEP1222"
    path.write_text(json.dumps(receipt), encoding="utf8")
    with pytest.raises(ValueError):
        physical_input_packet(root)
