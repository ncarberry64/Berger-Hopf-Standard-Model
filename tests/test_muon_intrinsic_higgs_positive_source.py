"""Literal source variation and complete angular-image checks."""
import numpy as np
import pytest
from bhsm.interface.muon_intrinsic_higgs_positive_source import (
    higgs_magnetic_source_image_space,intrinsic_higgs_positive_source_application,
)


@pytest.fixture(scope='module')
def actual():
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    fields=magnetic_open_fields_at_node(b,b['source']['times'][2])
    rep=dict(b['representation'],native_positive_nu_squared_action=b['receipt']['action_parameters']['nu_squared_action'])
    angular=retained_full_q_angular_space(ROOT)
    r=intrinsic_higgs_positive_source_application(fields['raw_fields'],rep,angular,
        length=b['receipt']['chronological_response_span'],
        first_wall_gauge=fields['first_wall_gauge'][:3],first_H=fields['first_H'][:3])
    return fields,rep,angular,r


def test_actual_source_keeps_complete_even_image_and_both_placements(actual):
    fields,rep,angular,r=actual
    assert r['source_n3_exactly_zero']
    assert {l[0] for l in r['even_harmonic_labels']}=={0,2,4}
    assert r['positive_H_even'].shape==(140,140)
    assert r['delta_positive_H_even_odd'].shape==(3,140,80)
    assert np.linalg.norm(r['delta_positive_H_even_odd'])>0
    assert np.linalg.norm(r['delta_potential_even_odd'])>0
    np.testing.assert_array_equal(r['delta_positive_H_even_odd'],sum(r[k] for k in (
        'delta_temporal_connection_even_odd','delta_spatial_even_odd','delta_potential_even_odd')))
    assert np.max(r['scalar_product_image_residual'])<2e-14
    assert r['both_covariant_derivative_placements_retained']
    assert r['physical_a_mu'] is None


def test_any_n3_coordinate_enriches_image_without_tolerance_deletion(actual):
    fields,rep,angular,r=actual
    # CONTROL_ONLY supplied source coordinate; not a physical field/state.
    a=np.zeros((1,5,4,20));h=np.zeros((1,4,20));h[0,1,4]=np.nextafter(0.,1.)
    image=higgs_magnetic_source_image_space(angular,a,h)
    assert not image['source_n3_exactly_zero']
    assert len(image['even_harmonic_labels'])==84
    n6=[i for i,l in enumerate(image['even_harmonic_labels']) if l[0]==6]
    assert np.linalg.norm(image['gaunt_even_odd_source'][n6,:,4:])>1
    assert np.max(image['scalar_product_image_residual'])<5e-14


def test_actual_variation_agrees_with_independent_literal_weak_pairing(actual):
    fields,rep,angular,r=actual
    from bhsm.interface.muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation
    from bhsm.interface.muon_current_source_motion_cubic import current_face_source_jets
    from bhsm.interface.muon_parent_maxwell_full_weak import M
    raw=fields['raw_fields'];weights=current_face_source_jets(raw[:100])['intrinsic_weights']
    wt,ws,wv=[weights[k].value for k in ('wT','wS','wV')]
    A=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180]);A[2:]+=M*(weights['mechanical_connection_lambda'].value-1)
    T=higgs_u2_real_representation()['real_generators'];H=raw[-8:-4]
    rng=np.random.default_rng(4201) # CONTROL_ONLY weak test coefficients.
    e=rng.normal(size=(4,35));o=rng.normal(size=(4,20));e/=np.linalg.norm(e);o/=np.linalg.norm(o)
    E,O,S=(r[k] for k in ('even_basis_values','odd_basis_values','source_basis_values'))
    ev,ov=E@e.T,O@o.T
    de=np.einsum('ph,ihk,ck->pic',E,r['even_derivative_matrices'],e)
    do=np.einsum('ph,ihk,ck->pic',O,r['odd_derivative_matrices'],o)
    # Literal pointwise covariant action, independently of Gaunt projection.
    da=np.einsum('ph,fch->pfc',S,r['source_wall_gauge'][0])
    dh=S@r['source_H'][0].T
    lam,nu=rep['scalar_matching']['lambda_H'],rep['native_positive_nu_squared_action']
    def cross_action(epsilon):
        omega=np.einsum('pfc,cuv->pfuv',A[None]+epsilon*da,T)
        te=np.einsum('puv,pv->pu',omega[:,0],ev);to=np.einsum('puv,pv->pu',omega[:,0],ov)
        se=de+np.einsum('piuv,pv->piu',omega[:,2:],ev)
        so=do+np.einsum('piuv,pv->piu',omega[:,2:],ov)
        h=H[None]+epsilon*dh
        potential=lam*(4*np.einsum('pu,pv->puv',h,h)+2*(np.sum(h*h,axis=1)-nu)[:,None,None]*np.eye(4))
        density=(wt/wv)*np.sum(te*to,axis=1)+(ws/wv)*np.sum(se*so,axis=(1,2))+np.einsum('pu,puv,pv->p',ev,potential,ov)
        return r['Haar_weights']@density
    exact=e.ravel()@r['delta_positive_H_even_odd'][0]@o.ravel()
    step=2e-5;fd=(cross_action(step)-cross_action(-step))/(2*step)
    assert fd==pytest.approx(exact,rel=2e-7,abs=2e-9)


def test_incomplete_fields_cannot_be_projected_or_zero_filled(actual):
    fields,rep,angular,r=actual
    with pytest.raises(ValueError,match='complete real'):
        higgs_magnetic_source_image_space(angular,fields['first_wall_gauge'][:3,:,:,:4],fields['first_H'][:3])
