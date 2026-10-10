"""Actual fixed-core operator derivative checks, without a physical c choice."""
import numpy as np
from scipy.special import exp1
from bhsm.interface.muon_native_coupled_source_heat import retained_corrected_scalar_photon_response
from bhsm.interface.muon_native_higgs_mean_heat_adjoint import corrected_mean_higgs_heat_cotangent
from bhsm.interface.muon_native_mean_core_heat_target import corrected_joint_mean_heat_cotangent,corrected_even_y_paired_heat_cotangent,_cutoff_divided_differences,_unit_lepton_mass6
from bhsm.interface.muon_native_product_factor_graph import _source_core_samples,_family_shell_heat_forms,lepton_unit_trace_gauge_representation
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian,lepton_current_hilbert_representation
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_parent_gauge_geometry_correction import finite_common_iterate_at_time
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


def test_full_cotangent_reproduces_owned_mean_h_target_and_material_rate_zeros():
    r=retained_corrected_scalar_photon_response();kw=dict(time_nodes=np.linspace(-.001,0,5),quadrature_order=3,parameter=4.7240808471919143e-8,integrate_cutoff=True,family_indices=(0,))
    old=corrected_mean_higgs_heat_cotangent(r,**kw);new=corrected_joint_mean_heat_cotangent(r,**kw)
    a=new['families']['0']['weighted_raw228_cotangent']
    np.testing.assert_allclose(a[:,220:224],old['families']['0']['weighted_mean_H_cotangent'],rtol=2e-12,atol=1e-30)
    assert np.count_nonzero(a[:,160:220])==0 and np.count_nonzero(a[:,224:])==0
    assert np.linalg.norm(a[:,:100])>0
    assert new['positive_Haar_density_applied_once']


def test_metric_measure_and_operator_jet_match_generalized_heat_derivative():
    r=retained_corrected_scalar_photon_response();nodes=np.linspace(-.001,0,5);c=4.7240808471919143e-8
    target=corrected_joint_mean_heat_cotangent(r,time_nodes=nodes,quadrature_order=3,parameter=c,family_indices=(0,))
    samples=_source_core_samples(r['coefficients'],r['representation'],r['reference'],nodes,np.ones((5,8)),3)
    fiber=np.array([0,1,6,7,12,13]);frame=lepton_current_hilbert_representation();G=lepton_unit_trace_gauge_representation()['generators']
    alpha=frame['alpha'];gamma5=frame['gamma5'];values=[]
    for eps in (-1e-6,1e-6):
        changed=[]
        for s in samples:
            t=nodes[s['cell']]+s['x']*s['h'];data=finite_common_iterate_at_time(t,r['coefficients'],r['representation'],r['reference'],rho=np.array([WALL]))
            q=data['q'].copy();q[0]+=eps;m=data['m'].copy();m[0]+=eps
            g=intrinsic_m4_weight_jet(12,q,data['qdot'],m,source_value=data['normal'],source_rate=data['normal_rate'])
            base=intrinsic_m4_weight_jet(12,data['q'],data['qdot'],data['m'],source_value=data['normal'],source_rate=data['normal_rate'])
            from bhsm.interface.muon_native_product_factor_graph import finite_common_family_intrinsic_operator
            op=finite_common_family_intrinsic_operator(t,r['coefficients'],r['representation'],r['reference'])
            N,R,lam=g['induced_lapse'].value,g['R4'].value,g['mechanical_connection_lambda'].value
            field=data['fields']['gauge'][0,0];omega=np.einsum('pa,aij->pij',field[2:]+M*(lam-1),G)
            W=1.5*gamma5/R+sum(-1j*alpha[a]@omega[a]/R for a in range(3))+fixed_y_higgs_hamiltonian(op['H'][None])[0]
            v=dict(s,N=N,R=R,W=W,weight=s['weight']*N/base['induced_lapse'].value);changed.append(v)
        eig=_family_shell_heat_forms(changed,5,None,fiber)['eigenvalues'];values.append(float(np.sum(exp1(c*eig))))
    derivative=(values[1]-values[0])/2e-6
    owned=target['families']['0']['constant_raw228_cotangent'][0]+target['families']['0']['constant_raw228_cotangent'][74]
    np.testing.assert_allclose(owned,derivative,rtol=3e-6,atol=2e-10)


def test_repeated_pole_divided_differences_and_LR_evenness_are_exactly_handled():
    lam=np.array([2.,2.,2.]);c=.3;first,second=_cutoff_divided_differences(lam,c,32)
    gp=np.exp(-c*2)*(c/2+1/4)
    gpp=-np.exp(-c*2)*(c*c/2+2*c/4+2/8)
    np.testing.assert_allclose(first,gp,rtol=2e-15)
    np.testing.assert_allclose(second,gpp/2,rtol=2e-15)
    M=_unit_lepton_mass6([1+2j,-.4+.7j]);sign=np.diag([1]*4+[-1]*2)
    np.testing.assert_array_equal(sign@M@sign,-M)


def test_stable_actual_paired_mass_target_matches_resolved_H_component():
    r=retained_corrected_scalar_photon_response();kw=dict(time_nodes=np.linspace(-.001,0,5),quadrature_order=3,parameter=4.7240808471919143e-8)
    stable=corrected_even_y_paired_heat_cotangent(r,**kw);literal=corrected_joint_mean_heat_cotangent(r,**kw)
    wanted=literal['families']['1']['constant_raw228_cotangent'][221]-literal['families']['2']['constant_raw228_cotangent'][221]
    actual=stable['families']['middle_minus_light']['constant_raw228_cotangent'][221]
    np.testing.assert_allclose(actual,wanted,rtol=2e-8,atol=1e-26)
    assert stable['exact_LR_sign_grading_mass_residual']==0
    grading=stable['normalized_LR_sign_grading']
    assert grading.shape==stable['normalized_P0_eigenvalues'].shape
    np.testing.assert_array_equal(grading[:,None]*stable['normalized_P1']*grading[None,:],-stable['normalized_P1'])
    np.testing.assert_array_equal(grading[:,None]*stable['normalized_P2']*grading[None,:],stable['normalized_P2'])
    assert stable['paired_value_Y_fourth_analytic_majorant']<1e-24
    assert stable['paired_target_formed_without_subtracting_nearly_equal_family_outputs']
