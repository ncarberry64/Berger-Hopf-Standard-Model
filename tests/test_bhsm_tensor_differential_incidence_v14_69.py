from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.tensor_differential_incidence_v14_69 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    sym_basis, sym_coordinates, sym_from_coordinates, linear_map_matrix,
    kk_metric_from_quotient, horizontal_quotient_metric,
    horizontal_quotient_differential, horizontal_quotient_adjoint,
    seam_embedding, trace_metric, trace_differential, trace_adjoint,
    moving_trace_differential, round_metric8, generic_bundle_metric8,
    dq_matrix, trace_matrix, chain_matrix, finite_difference_dq_residual,
    dq_adjoint_residual, trace_adjoint_residual, tensor_rank_payload,
    round_shape_kernel_payload, round_common_tensor_lifts,
    heterogeneous_tensor_incidence_isometry, tensor_attachment_operator,
    tensor_incidence_payload, compatibility_jacobian_round, compatibility_reducibility_matrix,
    compatibility_payload, provenance_gate_payload, neutrino_kill_screen_payload,
    status_payload, completion_gate_payload, next_object_payload,
    artifact_payloads, materialize,
)
from bhsm.interface.completion.action_attachment_wentzell_v14_67 import attachment_response_roots


def test_version_and_verdict():
    assert VERSION == "v14.69"
    assert "TENSOR" in PRIMARY_VERDICT
    assert "NONROUND" in EXACT_NEXT_OBJECT


def test_symmetric_basis_dimension_and_orthonormality():
    for n in (4, 5, 8):
        b = sym_basis(n)
        assert len(b) == n * (n + 1) // 2
        gram = np.array([[np.sum(x*y) for y in b] for x in b])
        assert np.linalg.norm(gram - np.eye(len(b))) < 1e-13


def test_symmetric_coordinate_roundtrip():
    rng = np.random.default_rng(1)
    z = rng.normal(size=(5,5)); a = 0.5*(z+z.T)
    c = sym_coordinates(a)
    r = sym_from_coordinates(c, 5)
    assert np.linalg.norm(a-r) < 1e-13


def test_kk_constructor_recovers_quotient():
    q = np.diag([1.1,1.2,1.3,1.4,1.5])
    c = np.diag([1.4,1.8,2.1])
    b = np.arange(15,dtype=float).reshape(5,3)*0.003
    g = kk_metric_from_quotient(q,b,c)
    assert np.min(np.linalg.eigvalsh(g)) > 0
    assert np.linalg.norm(horizontal_quotient_metric(g)-q) < 1e-13


def test_round_quotient_is_horizontal_block():
    g = round_metric8()
    assert np.array_equal(horizontal_quotient_metric(g), np.eye(5))


def test_generic_quotient_is_spd():
    q = horizontal_quotient_metric(generic_bundle_metric8())
    assert np.min(np.linalg.eigvalsh(q)) > 0


def test_dq_round_mixed_and_vertical_variations_are_kernel():
    g = round_metric8()
    dg = np.zeros((8,8))
    dg[0,6]=dg[6,0]=1
    assert np.linalg.norm(horizontal_quotient_differential(g,dg)) == 0
    dg2 = np.zeros((8,8)); dg2[6,6]=1
    assert np.linalg.norm(horizontal_quotient_differential(g,dg2)) == 0


def test_dq_round_horizontal_variation_passes_through():
    g = round_metric8()
    dg = np.zeros((8,8)); dg[1,2]=dg[2,1]=0.3; dg[4,4]=0.7
    out = horizontal_quotient_differential(g,dg)
    assert np.linalg.norm(out-dg[:5,:5]) < 1e-14


def test_dq_finite_difference_generic():
    assert finite_difference_dq_residual() < 1e-7


def test_dq_adjoint_virtual_work():
    assert dq_adjoint_residual() < 1e-11


def test_trace_adjoint_virtual_work():
    assert trace_adjoint_residual() < 1e-11


def test_seam_embedding_is_isometric():
    t = seam_embedding()
    assert np.array_equal(t.T@t, np.eye(4))


def test_trace_is_top_left_block_on_round_embedding():
    g = np.arange(25,dtype=float).reshape(5,5)
    g = 0.5*(g+g.T)
    assert np.array_equal(trace_metric(g), g[:4,:4])


def test_trace_adjoint_is_zero_normal_extension():
    y = np.diag([1,2,3,4])
    a = trace_adjoint(y)
    assert np.array_equal(a[:4,:4], y)
    assert np.linalg.norm(a[4,:]) == 0
    assert np.linalg.norm(a[:,4]) == 0


def test_rank_dimensions_exact():
    dq = dq_matrix()
    tr = trace_matrix()
    ch = chain_matrix()
    assert dq.shape == (15,36)
    assert tr.shape == (10,15)
    assert ch.shape == (10,36)
    assert np.linalg.matrix_rank(dq,tol=1e-11) == 15
    assert np.linalg.matrix_rank(tr,tol=1e-11) == 10
    assert np.linalg.matrix_rank(ch,tol=1e-11) == 10


def test_round_dq_singular_values_all_one():
    s = np.linalg.svd(dq_matrix(),compute_uv=False)
    assert np.max(np.abs(s-1.0)) < 1e-13


def test_round_trace_singular_values_all_one():
    s = np.linalg.svd(trace_matrix(),compute_uv=False)
    assert np.max(np.abs(s-1.0)) < 1e-13


def test_generic_dq_still_surjective():
    assert np.linalg.matrix_rank(dq_matrix(generic_bundle_metric8()),tol=1e-11) == 15


def test_round_shape_kernel_exact():
    z5 = np.zeros((5,5)); k0=np.zeros((4,4))
    assert np.linalg.norm(moving_trace_differential(z5,0.8,k0)) == 0


def test_nonzero_extrinsic_curvature_activates_shape_response():
    z5=np.zeros((5,5)); k=np.diag([0.1,0.02,-0.03,0.05])
    out=moving_trace_differential(z5,0.4,k)
    assert np.linalg.norm(out)>0
    assert np.linalg.norm(out-0.8*k)<1e-14


def test_reflected_extrinsic_curvatures_give_opposite_shape_response():
    z5=np.zeros((5,5)); k=np.diag([0.1,0.02,-0.03,0.05])
    p=moving_trace_differential(z5,0.4,k)
    m=moving_trace_differential(z5,0.4,-k)
    assert np.linalg.norm(p+m)<1e-14


def test_tensor_rank_payload():
    p=tensor_rank_payload()
    assert p["round_DQ_H_rank"]==15
    assert p["round_DQ_H_kernel_dimension"]==21
    assert p["trace_rank"]==10
    assert p["trace_kernel_dimension"]==5
    assert p["trace_after_DQ_H_rank"]==10
    assert p["generic_DQ_H_finite_difference_residual"]<1e-7
    assert p["DQ_H_adjoint_virtual_work_residual"]<1e-11
    assert p["trace_adjoint_virtual_work_residual"]<1e-11


def test_shape_payload_fail_closed():
    p=round_shape_kernel_payload()
    assert p["pure_normal_round_response_norm"]==0
    assert p["generic_nonzero_K_response_norm"]>0
    assert p["reflected_cap_response_sum_norm"]<1e-14
    assert p["three_nonuniform_shape_channels_derived_from_round_first_variation"] is False


def test_individual_common_tensor_lifts_are_isometric():
    lifts=round_common_tensor_lifts()
    assert lifts["M8"].shape==(36,10)
    assert lifts["M5_plus"].shape==(15,10)
    assert lifts["M5_minus"].shape==(15,10)
    assert lifts["M4"].shape==(10,10)
    for v in lifts.values():
        assert np.linalg.norm(v.T@v-np.eye(10))<1e-13


def test_heterogeneous_tensor_incidence_isometry():
    e=heterogeneous_tensor_incidence_isometry()
    assert e.shape==(76,20)
    assert np.linalg.matrix_rank(e,tol=1e-11)==20
    assert np.linalg.norm(e.conj().T@e-np.eye(20))<1e-12


def test_tensor_attachment_operator_rank_and_psd():
    w=tensor_attachment_operator()
    ev=np.linalg.eigvalsh(w)
    assert w.shape==(76,76)
    assert np.linalg.norm(w-w.conj().T)<1e-12
    assert np.min(ev)>-1e-12
    assert np.linalg.matrix_rank(w,tol=1e-11)==20


def test_tensor_attachment_nonzero_spectrum_matches_attachment_roots_x10():
    w=tensor_attachment_operator()
    ev=np.linalg.eigvalsh(w)
    nz=ev[ev>1e-11]
    expected=np.sort(np.repeat(np.asarray(attachment_response_roots()),10))
    assert len(nz)==20
    assert np.max(np.abs(nz-expected))<1e-11


def test_tensor_incidence_payload():
    p=tensor_incidence_payload()
    assert p["heterogeneous_boundary_metric_dimension"]==76
    assert p["attachment_tensor_subspace_dimension"]==20
    assert p["global_tensor_incidence_rank"]==20
    assert p["global_tensor_incidence_isometry_residual"]<1e-11
    assert p["tensor_Wentzell_rank"]==20
    assert p["nonzero_spectrum_matches_attachment_roots_x10_residual"]<1e-11
    assert p["full_gauge_fixed_calderon_space_closed"] is False


def test_round_compatibility_jacobian_shape_rank_and_shape_nulls():
    j=compatibility_jacobian_round()
    assert j.shape==(50,78)
    assert np.linalg.matrix_rank(j,tol=1e-11)==40
    r=compatibility_reducibility_matrix()
    assert r.shape==(10,50)
    assert np.linalg.matrix_rank(r,tol=1e-11)==10
    assert np.linalg.norm(r@j)<1e-12
    xp=np.zeros(78);xp[76]=1
    xm=np.zeros(78);xm[77]=1
    assert np.linalg.norm(j@xp)==0
    assert np.linalg.norm(j@xm)==0


def test_compatibility_payload():
    p=compatibility_payload()
    assert p["round_two_cap_compatibility_rank"]==40
    assert p["round_two_cap_compatibility_nullity"]==38
    assert p["constraint_row_redundancy_dimension"]==10
    assert p["reducibility_matrix_rank"]==10
    assert p["reducibility_identity_residual"]<1e-12
    assert p["pure_xi_plus_constraint_residual_norm"]==0
    assert p["pure_xi_minus_constraint_residual_norm"]==0
    assert p["compatibility_adjoint_virtual_work_residual"]<1e-11
    assert p["complete_physical_constraint_operator_derived"] is False


def test_provenance_gate_fails_closed():
    p=provenance_gate_payload()
    assert p["DQ_H_tensor_formula_derived"] is True
    assert p["round_first_shape_kernel_proved"] is True
    assert p["all_physical_provenance_inputs_present"] is False


def test_neutrino_kill_screen_blocks():
    p=neutrino_kill_screen_payload()
    assert p["physical_execution_allowed"] is False
    assert p["current_result"]=="PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_mass_PMNS_splitting_or_probability_emitted"] is False


def test_status_hindsight_ledger():
    p=status_payload()
    assert len(p["validated"])>=12
    assert len(p["invalidated"])>=4
    assert len(p["reclassified"])>=4
    assert len(p["open"])>=10
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["USB_touched"] is False


def test_completion_gate_passes_internal_but_fails_physical():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["physical_execution_allowed"] is False


def test_next_object_is_nonround_or_second_shape():
    p=next_object_payload()
    assert "NONROUND" in p["exact_next_object"]
    assert "second shape" in " ".join(p["why"]).lower()


def test_artifact_payload_count_and_names():
    p=artifact_payloads()
    assert len(p)==9
    assert "BHSM_completion_gate_v14_69.json" in p
    assert "BHSM_round_shape_kernel_v14_69.json" in p


def test_materialization_is_byte_deterministic(tmp_path: Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
