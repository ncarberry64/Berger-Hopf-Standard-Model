from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.global_attachment_incidence_curvature_v14_68 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT, V10_PROXY,
    core_stationary_radius, core_global_curvature,
    global_scale_action_derivatives, schur_effective_curvature,
    depth_global_curvature, scalar_stratum_incidence_map,
    tangent_stratum_incidence, canonical_incidence_isometry,
    incidence_projector, boundary_attachment_operator,
    coupled_wentzell_extension_matrices, sample_coupled_wentzell_domain_data,
    coupled_wentzell_diagnostics, incidence_response_operator,
    incidence_response_gauge_covariance_residual,
    global_curvature_payload, incidence_map_payload, coupled_wentzell_payload,
    operator_insertion_payload, provenance_gate_payload,
    neutrino_kill_screen_payload, status_payload, completion_gate_payload,
    next_object_payload, artifact_payloads, materialize,
)
from bhsm.interface.completion.action_attachment_wentzell_v14_67 import (
    H_CORE_REPRESENTATIVE, attachment_response_roots, tangent_basis,
    constraint_jacobian,
)
from bhsm.interface.completion.operator_valued_calderon_wentzell_v14_66 import boundary_green_form


def test_version_and_next_object():
    assert VERSION == "v14.68"
    assert "GLOBAL_ENVELOPMENT" in PRIMARY_VERDICT
    assert "FULL_TENSOR" in EXACT_NEXT_OBJECT


def test_core_stationary_radius_satisfies_exact_first_derivative_relation():
    k,a2,a8 = 1.7, 3.2, 8.9
    r = core_stationary_radius(k,a2,a8)
    assert abs(5*k*a2*r**4-a8/r**2) < 1e-12


def test_core_curvature_positive_for_positive_inputs():
    r, stiff, mass, h = core_global_curvature(1.2, 2.3, 5.4, 1.1, 3.2)
    assert r > 0 and stiff > 0 and mass > 0 and h > 0


def test_v10_proxy_reproduces_v11_4_h_core():
    *_, h = core_global_curvature(**V10_PROXY)
    assert abs(h-H_CORE_REPRESENTATIVE) < 1e-14


def test_global_scale_derivatives_match_finite_difference():
    x=0.13
    powers={8:0.04,6:-0.03,3:0.02}
    z=-0.17
    v,d1,d2=global_scale_action_derivatives(x,powers,z)
    eps=1e-5
    vp=global_scale_action_derivatives(x+eps,powers,z)[0]
    vm=global_scale_action_derivatives(x-eps,powers,z)[0]
    fd1=(vp-vm)/(2*eps)
    fd2=(vp-2*v+vm)/(eps*eps)
    assert abs(d1-fd1) < 1e-8
    assert abs(d2-fd2) < 2e-5


def test_log_term_contributes_first_but_not_second_derivative():
    _,d1a,d2a=global_scale_action_derivatives(0.2,{3:0.5},0.0)
    _,d1b,d2b=global_scale_action_derivatives(0.2,{3:0.5},0.71)
    assert abs((d1b-d1a)-0.71) < 1e-15
    assert d2a == d2b


def test_schur_effective_curvature_matches_manual_formula():
    h=np.array([[3.0,0.2,-0.1],[0.2,2.0,0.3],[-0.1,0.3,1.7]])
    eff=schur_effective_curvature(h,0)
    manual=h[0,0]-h[0,1:]@np.linalg.solve(h[1:,1:],h[1:,0])
    assert abs(eff-manual) < 1e-14


def test_schur_curvature_invariant_under_interior_basis_change():
    direct=2.4
    c=np.array([0.31,-0.17])
    hi=np.array([[2.2,0.2],[0.2,1.9]])
    h=np.block([[np.array([[direct]]), c[None,:]],[c[:,None],hi]])
    e1=schur_effective_curvature(h,0)
    t=np.array([[1.3,0.2],[-0.1,0.8]])
    hi2=t.T@hi@t
    c2=t.T@c
    h2=np.block([[np.array([[direct]]), c2[None,:]],[c2[:,None],hi2]])
    e2=schur_effective_curvature(h2,0)
    assert abs(e1-e2) < 1e-13


def test_depth_global_curvature_reduces_to_direct_when_decoupled():
    powers={8:0.04,6:-0.03,3:0.02}
    direct=global_scale_action_derivatives(0.0,powers,-0.2)[2]
    assert depth_global_curvature(0.0,powers,-0.2) == direct


def test_depth_global_curvature_schur_reduces_when_coupled():
    powers={8:0.04,6:-0.03,3:0.02}
    direct=depth_global_curvature(0.0,powers,-0.2)
    eff=depth_global_curvature(0.0,powers,-0.2,np.array([0.2]),np.array([[2.0]]))
    assert eff < direct
    assert eff > 0


def test_incidence_map_exact_structure():
    j0=scalar_stratum_incidence_map()
    expected=np.array([[1,0,0],[0,1,0],[0,1,0],[0,1,0]],float)
    assert np.array_equal(j0,expected)


def test_tangent_incidence_is_constraint_compatible_and_rank_two():
    n=tangent_basis()
    assert np.linalg.norm(constraint_jacobian()@n)==0
    j=tangent_stratum_incidence()
    assert np.array_equal(j,np.array([[1,1],[1,0],[1,0],[1,0]],float))
    assert np.linalg.matrix_rank(j)==2


def test_canonical_incidence_isometry_is_exact():
    e=canonical_incidence_isometry()
    assert e.shape==(4,2)
    assert np.linalg.norm(e.conj().T@e-np.eye(2)) < 1e-13


def test_incidence_projector_is_rank_two_orthogonal_projector():
    p=incidence_projector()
    assert np.linalg.norm(p-p.conj().T)<1e-13
    assert np.linalg.norm(p@p-p)<1e-13
    assert np.linalg.matrix_rank(p,tol=1e-12)==2


def test_boundary_attachment_operator_nonzero_spectrum_matches_roots():
    d=6
    w=boundary_attachment_operator(d)
    ev=np.linalg.eigvalsh(w)
    nz=ev[ev>1e-11]
    expected=np.sort(np.repeat(np.asarray(attachment_response_roots()),d))
    assert w.shape==(24,24)
    assert len(nz)==12
    assert np.max(np.abs(nz-expected)) < 1e-12


def test_boundary_attachment_operator_is_psd_rank_2d():
    d=5
    w=boundary_attachment_operator(d)
    assert np.linalg.norm(w-w.conj().T)<1e-13
    assert np.min(np.linalg.eigvalsh(w)) > -1e-12
    assert np.linalg.matrix_rank(w,tol=1e-11)==2*d


def test_coupled_wentzell_extension_self_adjoint():
    d=6
    w=boundary_attachment_operator(d)
    a,b=coupled_wentzell_extension_matrices(d,w)
    assert a.shape==(48,48)
    assert np.linalg.matrix_rank(np.concatenate((a,b),axis=1))==48
    assert np.linalg.norm(a@b.conj().T-b@a.conj().T)<1e-11


def test_coupled_wentzell_green_form_vanishes():
    d=6
    w=boundary_attachment_operator(d)
    f0,f1=sample_coupled_wentzell_domain_data(d,w,1468)
    g0,g1=sample_coupled_wentzell_domain_data(d,w,1469)
    assert abs(boundary_green_form(f0,f1,g0,g1))<1e-10


def test_coupled_wentzell_diagnostics_pass():
    p=coupled_wentzell_diagnostics(6)
    assert p["boundary_dimension"]==48
    assert p["vertex_operator_dimension"]==24
    assert p["vertex_Wentzell_rank"]==12
    assert p["self_adjoint_extension_pass"] is True


def test_incidence_response_is_positive_hermitian_without_dimension_doubling():
    h,m,w=incidence_response_operator()
    assert h.shape==(24,24)
    assert m.shape==(24,24)
    assert w.shape==(24,24)
    assert np.linalg.norm(h-h.conj().T)<1e-11
    assert np.min(np.linalg.eigvalsh(h))>0


def test_incidence_response_gauge_covariance_when_attachment_transport_transforms():
    assert incidence_response_gauge_covariance_residual() < 1e-11


def test_global_curvature_payload_is_fail_closed():
    p=global_curvature_payload()
    assert p["v10_radial_truncation"]["match_residual"] < 1e-14
    assert p["diagnostic_stationarity_residual"] < 1e-14
    assert p["diagnostic_schur_depth_curvature"] > 0
    assert p["diagnostic_interior_basis_change_residual"] < 1e-13
    assert p["historical_k_D_equals_1_promoted_to_physical"] is False
    assert p["physical_numerical_h_C_derived"] is False
    assert p["physical_numerical_k_D_derived"] is False


def test_incidence_payload_closes_only_reduced_symmetric_map():
    p=incidence_map_payload()
    assert p["J_rank"]==2
    assert p["E_star_E_residual"]<1e-13
    assert p["reduced_symmetric_incidence_map_closed"] is True
    assert p["full_tensor_DQ_H_and_trace_maps_evaluated_on_physical_background"] is False
    assert p["uniform_per_vertex_placement_required"] is False
    assert p["attachment_mode_dimension_doubling_required"] is False


def test_coupled_wentzell_payload_supersedes_uniform_theorem_lift_only_in_reduced_sector():
    p=coupled_wentzell_payload()
    assert p["rank_actual"]==p["rank_expected_2d"]==12
    assert p["nonzero_spectrum_matches_attachment_roots_residual"]<1e-12
    assert p["self_adjoint_domain"]["self_adjoint_extension_pass"] is True
    assert p["v14_67_uniform_vertex_lift_superseded_in_reduced_symmetric_sector"] is True
    assert p["full_physical_tensor_incidence_claim"] is False


def test_operator_payload_reduces_dimension_and_remains_finite():
    p=operator_insertion_payload()
    assert p["response_dimension"]==24
    assert p["no_mode_dimension_doubling"] is True
    assert p["response_minimum_eigenvalue"]>0
    assert p["attachment_operator_rank"]==12
    assert p["vertex_gauge_covariance_residual_when_attachment_transport_is_transformed"]<1e-11
    assert math.isfinite(p["diagnostic_heat_trace_increment"])
    assert math.isfinite(p["diagnostic_logdet_increment"])
    assert p["actual_physical_M8_M5_M4_tangential_operators_inserted"] is False


def test_provenance_gate_still_fails_closed():
    p=provenance_gate_payload()
    assert p["global_curvature_functionals_derived"] is True
    assert p["reduced_symmetric_incidence_map_derived"] is True
    assert p["canonical_incidence_Wentzell_lift_derived"] is True
    assert p["all_physical_provenance_inputs_present"] is False


def test_neutrino_kill_screen_blocks():
    p=neutrino_kill_screen_payload()
    assert p["physical_execution_allowed"] is False
    assert p["current_result"]=="PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_mass_PMNS_splitting_or_probability_emitted"] is False


def test_status_ledger_hindsight_categories():
    p=status_payload()
    assert len(p["validated"])>=10
    assert len(p["invalidated"])>=4
    assert len(p["reclassified"])>=4
    assert len(p["open"])>=10


def test_completion_gate_fails_closed_usb_untouched():
    p=completion_gate_payload()
    assert p["full_BHSM_complete"] is False
    assert p["mark_III"]=="NOT_REACHED"
    assert p["usb_touched"] is False
    assert p["global_h_C_functional_derived"] is True
    assert p["global_k_D_Schur_functional_derived"] is True
    assert p["reduced_symmetric_incidence_map_closed"] is True
    assert p["physical_full_tensor_incidence_closed"] is False


def test_next_object_is_full_tensor_evaluation_not_scalar_incidence_guess():
    p=next_object_payload()
    assert "full tensor" in p["highest_upstream_blocker"]
    assert p["postcomparison_choice_forbidden"] is True


def test_artifact_set_complete():
    p=artifact_payloads()
    assert len(p)==10
    assert "BHSM_completion_gate_v14_68.json" in p


def test_materialize_byte_deterministic(tmp_path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
