"""Publication replay and physical-input boundary checks."""
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "incoming_parent_trace_replay",
    ROOT / "scripts/replay_muon_birth_incoming_parent_trace_response.py")
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


def test_new_normalized_entry_enclosures_do_not_fill_the_physical_solver(tmp_path):
    result = REPLAY.materialize(tmp_path)
    packet = json.loads((tmp_path / "incoming_parent_trace_response.json").read_text())
    point = packet["preserved_point_inputs"]
    assert point["first_unavailable"] == dict(
        argument="parent_jet", operand="P_F", derivative_order=0, tuple_index=0)
    assert all(value is None for jet in point["solver_inputs"].values() for value in jet)
    assert point["point_KKT_callback_called"] is False
    assert point["point_noether_callback_called"] is False
    assert result["physical_parent_point_value"] is None
    assert result["physical_LR_enclosure"] is None
    assert result["preserved_milestone_files"] == 72


def test_two_new_materializations_are_byte_identical(tmp_path):
    one, two = tmp_path / "one", tmp_path / "two"
    REPLAY.materialize(one)
    REPLAY.materialize(two)
    names = {p.name for p in one.iterdir()}
    assert names == {"incoming_parent_trace_response.json", "source_manifest.json", "output_hashes.json"}
    assert names == {p.name for p in two.iterdir()}
    assert all((one / name).read_bytes() == (two / name).read_bytes() for name in names)


def test_report_display_interval_is_outward_for_all_covered_shells():
    from bhsm.interface.muon_birth_parametric_carrier_bounds import (
        retained_carrier_bound_inputs, uniform_carrier_majorants)
    lower = Fraction("9.512785673430680e-16")
    upper = Fraction("8.237301494782404e-15")
    for n in range(4):
        source = retained_carrier_bound_inputs(
            ROOT, absolute_unit_radius_eigenvalue=Fraction(2*n+3, 2))
        values = uniform_carrier_majorants(**{
            key: Fraction(value) for key, value in source["parameters"].items()})
        assert lower <= values["scaled_Mf_lower"]
        assert upper >= values["scaled_Mf_upper"]


def test_exact_nonhermitian_complement_reaction_requires_multiplier_block():
    """CONTROL_ONLY: test the reduction claimed, with retarded asymmetry."""
    import sympy as sp
    h = sp.Matrix([[3, 2], [1, 4]])
    c = sp.Matrix([[1, 2]])
    full = h.row_join(c.T).col_join(c.row_join(sp.zeros(1)))
    rhs = sp.Matrix([-5, -6, 7])
    solution = full.inv()*rhs
    kept = sp.Matrix([[3, 1], [1, 0]])
    x, y = sp.Matrix([2, 2]), sp.Matrix([[1, 2]])
    reduced = kept-x*y/4
    reduced_rhs = sp.Matrix([-5, 7])+x*sp.Rational(6, 4)
    assert reduced.inv()*reduced_rhs == sp.Matrix([solution[0], solution[2]])
    assert reduced[1, 1] == -1
    assert x.T != y
    assert (kept-x*x.T/4).inv()*reduced_rhs != sp.Matrix([solution[0], solution[2]])
    # Deleting only the induced multiplier reaction makes this system singular.
    invalid = reduced.copy()
    invalid[1, 1] = 0
    assert invalid.det() == 0
