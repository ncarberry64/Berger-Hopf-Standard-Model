"""Inherited basis accounting and read-only carrier entry enclosure checks."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

import pytest
import sympy as sp

from bhsm.interface.muon_birth_incoming_parent_trace_response import (
    exact_chiral_frame_identity, incoming_parent_trace_packet,
    parent_consumer_sufficiency_contract, particle_trace_shell_basis,
    retained_carrier_shell_enclosure,
)
from bhsm.interface.muon_birth_parametric_carrier_bounds import uniform_carrier_majorants


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("n,dimension", [(0, 8), (1, 24), (2, 48), (3, 80), (7, 288)])
def test_full_signed_shell_separates_weyl_spatial_and_conjugate_dimensions(n, dimension):
    rows = particle_trace_shell_basis(n)
    assert len(rows) == dimension
    assert Counter(r["squared_factor_sign"] for r in rows) == {-1: dimension//2, 1: dimension//2}
    assert len({(r["weyl"], r["spatial_dirac_sign"], r["angular_degeneracy_index"]) for r in rows}) == dimension
    assert all(r["internal_family_basis_vector"] == [0, 1, 0] for r in rows)
    assert all(r["physical_field_amplitude"] is None for r in rows)


def test_exact_gamma_transform_independently_exhibits_two_weyl_copies():
    result = exact_chiral_frame_identity()
    assert result["validation_passed"] is True
    u = sp.sympify(result["change_of_basis"], locals={"Matrix": sp.Matrix})
    sigma = sp.Matrix([[0, 1], [1, 0]])
    alpha = sp.BlockMatrix([[sp.zeros(2), sigma], [sigma, sp.zeros(2)]]).as_explicit()
    assert sp.simplify(u.H*alpha*u) == sp.diag(-sigma, sigma)


def test_n0_all_matrix_entries_are_present_and_carrier_only():
    shell = retained_carrier_shell_enclosure(ROOT, 0)
    entries = shell["explicit_scaled_8_by_8_entry_enclosures"]
    assert len(entries) == 8 and all(len(row) == 8 for row in entries)
    assert sum("exact" in entry for row in entries for entry in row) == 56
    assert sum("lower" in entry for row in entries for entry in row) == 8
    parameters = {k: Fraction(v) for k, v in shell["retained_inputs"]["parameters"].items()}
    inherited = uniform_carrier_majorants(**parameters)
    for i in range(8):
        assert Fraction(entries[i][i]["lower"]) == inherited["scaled_Mf_lower"]
        assert Fraction(entries[i][i]["upper"]) == inherited["scaled_Mf_upper"]
    assert shell["offdiagonal_zeros_are_full_LR_or_PF_zeros"] is False
    assert shell["physical_full_PF_order0"] is None


def test_n0_self_dual_maps_are_exact_representation_only():
    representation = retained_carrier_shell_enclosure(ROOT, 0)["self_dual_representation"]
    gram = sp.Matrix(representation["explicit_Gram"])
    gamma = sp.Matrix(representation["explicit_Gamma_linear_matrix"])
    grading = sp.Matrix(representation["explicit_charge_grading"])
    em_charge = sp.Matrix(representation["explicit_EM_charge"])
    assert gram == sp.eye(16)
    assert gamma.H*gamma == gram and gamma*gamma.conjugate() == gram
    assert gamma*grading+grading*gamma == sp.zeros(16)
    assert em_charge == -grading
    assert len(representation["explicit_basis_rows"]) == 16
    assert representation["covariance"] is None
    assert representation["full_parent_conjugate_statistics_lift"] is None


def test_complete_retained_packet_uses_shared_family_and_no_point_selection():
    packet = incoming_parent_trace_packet(ROOT)
    assert packet["shell_counts"]["particle_dimensions"] == [8, 24, 48, 80]
    assert packet["shell_counts"]["diagonal_pairings_enclosed"] == 160
    assert packet["shell_counts"]["exact_ordered_offdiagonal_pairings"] == 25440
    assert packet["shell_counts"]["exact_cross_shell_pairings"] == 16256
    family_parameters = [tuple(s["retained_inputs"]["parameters"][k] for k in ("a_lower", "a_upper", "lambda_upper"))
                         for s in packet["shells"]]
    assert len(set(family_parameters)) == 1
    assert packet["physical_amplitude_selected"] is False
    assert packet["physical_angular_cutoff_selected"] is False
    assert packet["point_KKT_solver_called"] is False
    assert packet["complete_physical_PF_order0"] is None
    assert packet["consumed_parent_status"]["order"] == 0
    assert packet["normalized_basis_contract"]["pointwise_dimension_is_full_angular_trace_dimension"] is False
    assert packet["consumer_sufficiency"]["one_scalar_p_dagger_R_r_supplies_full_parent_matrix"] is False
    assert packet["shells"][0]["self_dual_representation"]["full_parent_conjugate_statistics_lift"] is None
    json.dumps(packet)  # Direct deterministic producer consumer; no symbolic objects leak.
    for source in packet["source_records"]:
        assert sha256((ROOT/source["path"]).read_bytes()).hexdigest() == source["raw_sha256"]


@pytest.mark.parametrize("invalid", [None, True, -1, 1.5, Fraction(1)])
def test_basis_level_guard(invalid):
    with pytest.raises((TypeError, ValueError)):
        particle_trace_shell_basis(invalid)


def test_no_unstored_numerical_channel_is_manufactured():
    with pytest.raises(ValueError, match="No stored"):
        retained_carrier_shell_enclosure(ROOT, 4)


def test_full_retarded_kkt_complement_reduction_keeps_distinct_left_right_and_multiplier():
    """EXACT_ALGEBRA_ONLY: test the reduction, not a physical E1 operator."""
    h = sp.Matrix([[3, 2+sp.I], [1-sp.I, 4+sp.I]])
    c, j, d = sp.Matrix([[1, 2]]), sp.Matrix([1, 3]), sp.Integer(2)
    whole = h.row_join(c.H).col_join(c.row_join(sp.zeros(1)))
    full_solution = whole.inv()*sp.Matrix([-j[0], -j[1], d])
    kept = sp.Matrix([[h[0, 0], c[0, 0]], [c[0, 0], 0]])
    left, right = sp.Matrix([h[0, 1], c[0, 1]]), sp.Matrix([[h[1, 0], c[0, 1]]])
    reduced = kept-left*right/h[1, 1]
    rhs = sp.Matrix([-j[0], d])+left*j[1]/h[1, 1]
    answer = reduced.inv()*rhs
    assert sp.simplify(answer-sp.Matrix([full_solution[0], full_solution[2]])) == sp.zeros(2, 1)
    assert right != left.H  # The retarded block is not assumed Hermitian.
    assert sp.simplify(reduced[1, 1]+c[0, 1]**2/h[1, 1]) == 0
    assert reduced[1, 1] != 0
    naive = kept.inv()*sp.Matrix([-j[0], d])
    assert sp.simplify(answer-naive) != sp.zeros(2, 1)
    contract = parent_consumer_sufficiency_contract()["nonreducing_subspace_elimination"]
    assert contract["zero_multiplier_block_callback_accepts_general_reduction"] is False
