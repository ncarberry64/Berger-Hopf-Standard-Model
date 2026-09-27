"""Focused regression checks for the new coupled center and signed jet."""
import json
from pathlib import Path
import sys

import numpy as np
from flint import arb, ctx, fmpq

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import solve_n12_gate7_fiber_constrained_center as s
from certify_n12_gate7_coupled_center_neighborhood import load
from checkpoint_n12_gate7_66d_tangent_binding import digest

OUT=s.BASE/'gate7_coupled_fiber_center_20260927'


def report(name):
    return json.loads((OUT/name/'report.json').read_bytes())


def test_coupled_solve_reduces_actual_residual_without_projection():
    r=report('center');first,last=r['iterations'][0],r['iterations'][-1]
    assert first['fiber_left_physical']>9e-14
    assert last['residual_norm_upper']<2e-60
    assert last['fiber_left_physical']<3e-80
    assert max(last['constraint_left'],last['constraint_right'])<1e-64
    assert r['fiber_row_inside_solve'] and not r['post_solve_projection']
    assert not r['raw_eigenvalue_as_descriptor']


def test_all_selected_lines_have_owned_normalization_orientation_and_index():
    for proof in report('center')['endpoint_eigenpair_proofs']:
        assert proof['validation_passed']
        assert proof['normalized_eigenpair_enclosed']
        assert proof['positive_stored_reference_overlap']
        assert proof['selected_zero_based_index_verified']==24


def test_local_banach_inequalities_use_outward_rationals():
    ctx.prec=512;r=report('neighborhood')
    assert r['status']=='LOCAL_COUPLED_CENTER_NEIGHBORHOOD_CERTIFIED'
    for name in ('graph','fixed_label'):
        c=r[name];Y=fmpq(c['Y_upper']);Z=fmpq(c['Z_upper']);rho=fmpq(c['radius_exact'])
        assert 0<=Z<1
        assert Y+Z*rho<=fmpq(c['image_radius_upper'])<rho
        assert c['unique_root_in_declared_box']
    assert not r['old_physical_tube_covered']


def test_uniform_implicit_jet_keeps_fixed_label_and_signed_constraints():
    r=report('jet');a=load(OUT/'jet/arrays.npz');ctx.prec=512
    assert r['reduced_rank_diagnostic']==75
    assert 49<r['reduced_condition']<51
    assert r['fixed_label_rank_diagnostic']==66
    assert r['fixed_label_left_rank_certified_by_Gram_inverse']==66
    assert r['fixed_label_descriptor_variation']['exact_upper']=='0'
    assert fmpq(r['fixed_label_phase_slope_lower'])>0
    J=s.matrix(a['Jfixed125']);X=s.matrix(a['fixed_label_response']);F=s.matrix(a['forcing'])
    assert all(v.contains(0) for v in (J*X+F).entries())
    g=s.matrix(a['left_covector']);T=s.matrix(a['fixed_label_left_history'][:98])
    assert all(v.contains(0) for v in (g*T).entries())
    assert r['fixed_label_inverse_left_defect']['approximate_upper']<1
    assert r['fixed_label_inverse_right_defect']['approximate_upper']<1


def test_discretization_and_interface_residuals_are_retained():
    center=report('center')['iterations'][-1];jet=report('jet')
    assert 3e-12<center['shooting_full']<4e-12
    assert 1e-18<center['fiber_right_physical']<2e-18
    assert max(x['approximate_upper'] for x in jet['frozen_interface_response_row_norms'])>1e-2
    assert not jet['seven_nonlinear_boundary_rows_identified_with_HS']
    assert not jet['Layer_C_rebound']


def test_checkpoint_sources_and_deterministic_reproduction():
    for name in ('center','neighborhood','jet'):
        r=report(name)
        assert digest(OUT/name/'arrays.npz')==r['arrays_SHA256']
        assert not r['Gate7_closed'] and not r['FULL_BHSM_COMPLETE']
        assert not r['tolerances_changed']
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    for name,entry in receipt['files'].items():
        assert entry['byte_identical']
        assert digest(OUT/name)==entry['SHA256']


def test_phase_chart_dimension_requires_transverse_flow():
    # Independent small example: a phase outside the child subspace preserves
    # its dimension at fixed label, but changes the boundary data.
    T=np.eye(3)[:,:2];flow=np.array([1.,0.,1.]);g=np.array([[1.,0.,0.]])
    fixed=T-np.outer(flow,(g@T).ravel())/float((g@flow).item())
    assert np.linalg.matrix_rank(fixed)==2
    assert np.allclose(g@fixed,0)
    assert np.linalg.norm(np.array([[0.,0.,1.]])@fixed)>0
