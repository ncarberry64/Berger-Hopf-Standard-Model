from functools import lru_cache
import numpy as np

from bhsm.interface.muon_birth_chronological_boundary_action import discrete_boundary_two_jet
from bhsm.interface.muon_birth_chronological_canonical_graph import (
    canonical_boundary_step_action,chronological_canonical_graph,
    retained_chronological_canonical_graph,
)


def quadratic_action_cell(h):
    # The algebraic variable has a genuine nonzero mixed coupling. Its
    # elimination leaves L=.5v^2-.5*omega^2*x^2, omega^2=2+.3^2/1.7.
    H=np.array([[-2.,0.,.3],[0.,1.,0.],[.3,0.,1.7]])
    K=discrete_boundary_two_jet(H,np.zeros(3),h,1)['hessian']
    return H,K


def test_same_action_canonical_map_is_the_implicit_midpoint_hamiltonian_map():
    h=.17;H,K=quadratic_action_cell(h)
    a=canonical_boundary_step_action(K,1,action_hessian=H,positive_step=h)
    omega=2.+.3**2/1.7;generator=np.array([[0.,1.],[-omega,0.]])
    exact=np.linalg.solve(np.eye(2)-h*generator/2,np.eye(2)+h*generator/2)
    np.testing.assert_allclose(a['canonical_map'],exact,rtol=2e-16,atol=2e-16)
    assert a['stored_action_arithmetic_certificate']['framed_operator_certified_invertible']
    assert a['stored_action_arithmetic_certificate']['all_algebraic_equations_residual_upper']<1e-35
    assert np.max(abs(a['original_algebraic_defect']))<1e-15
    assert not a['physical_E0_boundary_or_normal_mode_selected']


def test_composition_keeps_the_canonical_dual_and_all_algebraic_lifts():
    h=.07;H,K=quadratic_action_cell(h)
    a=chronological_canonical_graph(np.array([K,K,K]),1,
        action_hessians=np.array([H,H,H]),positive_step=h)
    one=a['cell_applications'][0]['canonical_map']
    np.testing.assert_allclose(a['canonical_map'],one@one@one,rtol=3e-16,atol=3e-16)
    assert a['cell_full_boundary_algebraic_lifts'].shape==(3,3,2)
    assert a['compatibility_equations'].shape==(0,2)
    assert not a['initial_boundary_graph_replaced']


@lru_cache(maxsize=1)
def actual():
    return retained_chronological_canonical_graph(
        'artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_incoming_1steps_run_1')


def test_actual_named_frame_preserves_static_central_coordinates_and_original_rows():
    a=actual();b=a['cell_applications'][0];n=len(b['initial_coordinate_map'])
    # This material homogeneous action is exactly independent of static
    # central Ar values. A velocity frame must not reset those coordinates.
    rep=a['boundary_application']['representation']
    from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
    c=generic_coordinate_lift(rep['gauge_labels'])
    for j,i in enumerate(c['dynamic_gauge_indices']):
        if rep['gauge_labels'][i]['field']=='A_rho' and rep['gauge_labels'][i]['internal']==3:
            column=np.zeros(2*n);column[38+j]=1.
            np.testing.assert_allclose(b['canonical_map']@column,column,rtol=0,atol=3e-16)
            assert np.max(abs(b['compatibility_equations']@column))<1e-16
    assert b['spectral_directions_removed']==0
    assert b['true_Lyy_and_all_algebraic_rows_retained']
    assert np.max(abs(b['frame_defect']))<1e-15


def test_arb_encloses_stored_action_equations_without_symmetrizing_or_claiming_continuum():
    b=actual()['cell_applications'][0];cert=b['stored_action_arithmetic_certificate']
    assert cert['literal_equation_residual_upper']<1e-20
    assert cert['initial_canonical_reaction_identity_upper']<1e-20
    assert cert['reciprocity_after_explicit_action_antisymmetry_upper']<1e-16
    assert cert['retained_action_antisymmetry_reciprocity_term_upper']>0
    assert not cert['physical_continuum_or_producer_rounding_error_enclosed']
    assert np.max(b['canonical_map_export_error_upper'])<1e-10
    # Arbitrary canonical input columns are not declared physical: their
    # nonzero frame-reaction compatibility equations are returned.
    assert np.linalg.norm(b['compatibility_equations'])>1
