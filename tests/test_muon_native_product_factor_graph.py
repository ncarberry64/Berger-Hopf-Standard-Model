"""Actual finite-family component checks; no physical state/cutoff chosen."""
import hashlib
import numpy as np
import pytest
from scipy.linalg import solve, eigh
from scipy.integrate import quad

from bhsm.interface.muon_moving_geometric_action import retained_state
from bhsm.interface.muon_parent_gauge_geometry_correction import correction_representation, ROOT
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_native_product_factor_graph import (
    lepton_unit_trace_gauge_representation, finite_common_family_intrinsic_operator,
    finite_family_source_paired_core, finite_family_temporal_frame_transport,
    finite_family_retarded_source_transport, reset_graph_jet_in_temporal_frames,
    retained_eight_q_fermion_source_image, finite_family_eight_q_source_pairing,
    finite_eight_q_heat_core, finite_eight_q_heat_application,
    finite_eight_q_cutoff_heat_application, _ordered_heat_lag, _ordered_cutoff_heat_lag,
)


@pytest.fixture(scope='module')
def family():
    path=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/material_wall_mean_run_1/application.npz'
    assert hashlib.sha256(path.read_bytes()).hexdigest()=='4a16d56ec64eeb6c2db10000debf9695f24f7bef634e793011066ed88f8b9383'
    with np.load(path) as data:c=data['updated_coefficients']
    rep=correction_representation(time_points=8,radial_points=48,cap_points=48,
        radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    return c,rep,retained_state(ROOT)


def test_gauge_embedding_charge_and_internal_normalization():
    r=lepton_unit_trace_gauge_representation();g=r['generators']
    np.testing.assert_allclose(g[0]@g[1]-g[1]@g[0],g[2]/np.sqrt(2),atol=1e-16)
    np.testing.assert_allclose(1j*np.sqrt(2)*g[2]+1j*np.sqrt(10/3)*g[3],r['physical_EM_generator'],atol=1e-16)
    np.testing.assert_array_equal(g[:,12:,12:][:3],0)
    for alpha in lepton_current_hilbert_representation()['alpha']:
        np.testing.assert_allclose(alpha@g-g@alpha,0,atol=1e-16)


def test_actual_full_scalar_vector_moving_pullback_and_lapse(family):
    c,rep,ref=family
    d=finite_common_family_intrinsic_operator(-rep['length']/2,c,rep,ref)
    assert d['H'][1].real==pytest.approx(1.068072065839381,abs=1e-12)
    assert d['H'][0]!=0  # tiny charged component is retained, not forced to zero
    assert d['N']>0 and d['R4']>0
    np.testing.assert_allclose(d['Omega_tau_Lorentz']*d['N'],d['Omega_t'],atol=1e-35)
    np.testing.assert_allclose(d['H_can'],d['W']-1j*d['Omega_tau_Lorentz'],atol=1e-20)
    np.testing.assert_allclose(d['W'],d['W'].conj().T,atol=1e-16)
    assert 'not incoming temporal C1' in d['scope']


@pytest.fixture(scope='module')
def core(family):
    c,rep,ref=family
    nodes=np.linspace(-rep['length'],0,5)
    return finite_family_source_paired_core(coefficients=c,representation=rep,reference=ref,
        time_nodes=nodes,negative_spectral_parameter=-1,
        electromagnetic_coupling=np.sqrt(4*np.pi/137.035999206),spatial_photon_component=1,
        source_v_nodes=np.ones(5),source_J_nodes=np.ones(5),quadrature_order=3)


def test_full_two_endpoint_poisson_and_adjoint_graph(core):
    H,E=core['negative_axis_form'],core['Poisson_map']
    assert E.shape==(90,36)
    interior,boundary=core['interior_coefficient_indices'],core['boundary_coefficient_indices']
    residual=np.linalg.norm((H@E)[interior])/(np.linalg.norm(H)*np.linalg.norm(E))
    assert residual<2e-15
    direct=H[np.ix_(boundary,boundary)]-H[np.ix_(boundary,interior)]@solve(
        H[np.ix_(interior,interior)],H[np.ix_(interior,boundary)],assume_a='pos')
    np.testing.assert_allclose(core['paired_two_endpoint_graph'],direct,rtol=3e-14,atol=2e-9)
    np.testing.assert_allclose(core['two_insertion_Jv'],core['two_insertion_vJ'].conj().T,atol=1e-22)
    assert not core['physical_endpoint_or_reset_conditions_selected']
    assert not core['full_native_heat_or_Pauli_evaluated']


def test_source_square_and_both_nonzero_poisson_insertions_are_counted_once(core):
    expected=core['source_square_contact']-core['two_insertion_vJ']-core['two_insertion_Jv']
    np.testing.assert_allclose(core['graph_vJ'],expected,atol=1e-18)
    assert np.linalg.norm(core['source_square_contact'])>1e-3
    assert np.linalg.norm(core['two_insertion_vJ'])>1e-11
    # Independent source shift and fresh interior elimination.
    K,M=core['core_forms']['K'],core['core_forms']['M']
    Kv,Kvv=core['core_forms']['v'],core['core_forms']['vJ']
    b,i=core['boundary_coefficient_indices'],core['interior_coefficient_indices']
    def graph(s):
        H=K+M+s*Kv+.5*s*s*Kvv
        return H[np.ix_(b,b)]-H[np.ix_(b,i)]@solve(H[np.ix_(i,i)],H[np.ix_(i,b)],assume_a='pos')
    step=.2
    derivative=(graph(step)+graph(-step)-2*graph(0))/step**2
    assert np.linalg.norm(derivative-core['graph_vJ'])/np.linalg.norm(core['graph_vJ'])<1e-5


def test_actual_temporal_transport_and_advanced_adjoint(family):
    c,rep,ref=family;ts=np.linspace(-rep['length'],0,5)
    frame=finite_family_temporal_frame_transport(coefficients=c,representation=rep,reference=ref,
        times=ts,initial_frame=np.eye(18),rtol=1e-11,atol=1e-13)
    assert frame['unitarity_residual']<1e-12
    assert not frame['actual_reset_lift_selected']
    result=finite_family_retarded_source_transport(coefficients=c,representation=rep,reference=ref,
        times=ts,electromagnetic_coupling=np.sqrt(4*np.pi/137.035999206),
        spatial_photon_component=1,source_v_nodes=np.ones(5),source_J_nodes=np.ones(5),
        rtol=1e-11,atol=1e-13)
    assert result['unitarity_residual']<1e-11
    assert result['advanced_endpoint_identity_residual']<1e-10
    assert np.linalg.norm(result['retarded_vJ'][-1])>0
    U,Uv,Uj,Uvj=(result[k][-1] for k in ('retarded_fundamental','retarded_v','retarded_J','retarded_vJ'))
    np.testing.assert_allclose(Uvj.conj().T@U+Uv.conj().T@Uj+Uj.conj().T@Uv+U.conj().T@Uvj,0,atol=1e-14)


def test_reset_jet_keeps_holonomy_and_both_cross_orders():
    Q=lepton_current_hilbert_representation()['EM_charge']
    A=1j*.3*Q;B=1j*.4*Q;I=np.eye(18);Z=np.zeros((18,18),complex)
    phase=np.diag(np.exp(1j*.7*np.diag(Q)))
    R=dict(value=phase,v=A@phase,J=B@phase,vJ=A@B@phase)
    up=dict(value=I,v=2*A,J=3*B,vJ=6*A@B)
    uc=dict(value=I,v=4*A,J=5*B,vJ=20*A@B)
    result=reset_graph_jet_in_temporal_frames(owned_reset_jet=R,parent_frame_jet=up,child_frame_jet=uc)
    T=result['trace_map_jet']
    np.testing.assert_allclose(T['vJ'],(3*A)@(3*B)@phase,atol=1e-16)
    np.testing.assert_array_equal(result['positive_current_point_dual_jet']['vJ'],T['vJ'].conj().T)
    with pytest.raises(ValueError,match='all value/v/J/vJ'):
        reset_graph_jet_in_temporal_frames(owned_reset_jet={'value':I},parent_frame_jet=up,child_frame_jet=uc)


@pytest.fixture(scope='module')
def eight_q_core(family):
    c,rep,ref=family
    return finite_family_eight_q_source_pairing(coefficients=c,representation=rep,reference=ref,
        time_nodes=np.linspace(-rep['length'],0,5),negative_spectral_parameter=-1,
        source_beta_nodes=np.ones((5,8)),quadrature_order=3,repository=ROOT)


def test_actual_q_normalization_and_haar_source_pairing():
    source=retained_eight_q_fermion_source_image(ROOT)
    angular=source['angular']
    image=source['unit_radius_source_image'].reshape(8,20,18,18)
    np.testing.assert_allclose(source['raw_source_Gram'],(16/3)*np.eye(8),atol=2e-12)
    # Independent pointwise multiplication in the retained normalized basis.
    pointwise=np.einsum('ph,Ahij->Apij',angular['basis_values'],image)
    haar=np.einsum('p,Apki,Bpkj->ABij',angular['Haar_weights'],pointwise.conj(),pointwise)
    coefficients=np.einsum('Ahki,Bhkj->ABij',image.conj(),image)
    np.testing.assert_allclose(haar,coefficients,atol=2e-13)
    np.testing.assert_allclose(pointwise,pointwise.conj().transpose(0,1,3,2),atol=1e-14)
    # The owned eight-Q directions include weak charged-current generators.
    # A scalar EM charge vertex would erase this actual noncommuting part.
    Q=lepton_current_hilbert_representation()['EM_charge']
    assert np.linalg.norm(Q@pointwise-pointwise@Q)>1
    assert not source['extra_measured_e_or_old_T_b_applied']


def test_full_q_complement_is_used_and_both_orders_survive(eight_q_core):
    packet=eight_q_core
    assert packet['full_source_action_space_dimension']==378
    assert {k:v['full18_shell_dimension'] for k,v in packet['shell_applications'].items()}=={'1':72,'3':288}
    pair=packet['ordered_two_insertion']
    np.testing.assert_allclose(pair,pair.conj().transpose(1,0,3,2),atol=2e-21)
    expected=packet['source_square_contact']-pair-pair.transpose(1,0,2,3)
    np.testing.assert_allclose(packet['source_paired_graph_mixed'],expected,atol=1e-19)
    assert np.linalg.norm(pair)>1e-8
    assert packet['higher_n_source_directed_core_remainder']==0
    assert not packet['complete_native_heat_or_Pauli_evaluated']
    # The full response genuinely leaves the span of direct source images.
    # This detects the inadmissible substitution of an image-only inverse.
    image=packet['source']['unit_radius_source_image'].reshape(8,20,18,18)
    labels=packet['source']['angular']['harmonic_labels']
    for n,result in packet['shell_applications'].items():
        ids=[i for i,label in enumerate(labels) if label[0]==int(n)]
        size=18*len(ids)
        columns=image[:,ids].reshape(8,size,18).transpose(1,0,2).reshape(size,144)
        u,s,_=np.linalg.svd(columns,full_matrices=False)
        u=u[:,s>1e-12]
        response=result['complementary_Poisson_application'].reshape(3,size,288)
        outside=response-np.einsum('ij,tjk->tik',u@u.conj().T,response)
        assert np.linalg.norm(outside)/np.linalg.norm(response)>.01
        assert result['complementary_Poisson_residual_relative']<2e-15
        assert result['all_shell_columns_used'] and not result['eight_source_compression_used']


def test_complex_raw_source_profile_is_rejected(family):
    c,rep,ref=family
    with pytest.raises(ValueError,match='explicit real'):
        finite_family_eight_q_source_pairing(coefficients=c,representation=rep,reference=ref,
            time_nodes=np.linspace(-rep['length'],0,5),negative_spectral_parameter=-1,
            source_beta_nodes=np.ones((5,8),complex)+1j,quadrature_order=3,repository=ROOT)


@pytest.fixture(scope='module')
def heat_core(family):
    c,rep,ref=family
    return finite_eight_q_heat_core(coefficients=c,representation=rep,reference=ref,
        time_nodes=np.linspace(-rep['length'],0,3),source_beta_nodes=np.ones((3,8)),
        quadrature_order=3,repository=ROOT)


def test_complete_family_gram_and_heat_image(heat_core):
    assert set(heat_core['families'])=={'1','2'}
    for key,f in heat_core['families'].items():
        assert f['inherited_family']=={'1':'middle','2':'light'}[key]
        assert len(f['n0_eigenvalues'])==6 and np.min(f['n0_eigenvalues'])>0
        assert f['positive_Gram_orthogonality_residual']<1e-13
        assert {n:len(s['eigenvalues']) for n,s in f['intermediate_shells'].items()}=={'1':24,'3':96}
        for shell in f['intermediate_shells'].values():
            assert shell['generalized_eigen_residual_relative']<1e-14
            assert shell['all_complementary_eigenmodes_retained']
    assert not heat_core['physical_native_domain_closed']
    assert not heat_core['physical_cutoff_selected']


def test_duhamel_contact_and_both_orders_match_independent_spectral_second_derivative(heat_core):
    f=heat_core['families']['1'];lam=f['n0_eigenvalues'];s=1/lam[0]
    blocks=list(f['intermediate_shells'].values())
    spectrum=np.r_[lam,*[b['eigenvalues'] for b in blocks]]
    first=np.zeros((len(spectrum),len(spectrum)),complex);offset=len(lam)
    for block in blocks:
        F=block['first_jet_n0'][0]
        first[offset:offset+len(F),:len(lam)]=F
        first[:len(lam),offset:offset+len(F)]=F.conj().T
        offset+=len(F)
    second=np.zeros_like(first)
    # Off-diagonal second-jet entries do not enter a trace at the diagonal
    # base.  This independent spectral calculation uses actual action jets.
    second[:len(lam),:len(lam)]=np.diag(f['mixed_contact_n0_spectral_diagonal'][0,0])
    def trace_at(epsilon):
        values,vectors=eigh(np.diag(spectrum)+epsilon*first+.5*epsilon**2*second)
        return np.sum(np.sum(abs(vectors[:len(lam)])**2,axis=0)*np.exp(-s*values))
    finite_difference=trace_at(1)+trace_at(-1)-2*trace_at(0)
    app=finite_eight_q_heat_application(heat_core,s)['families']['1']
    expected=app['source_square_contact']+app['ordered_two_insertion']+app['opposite_order_two_insertion']
    np.testing.assert_allclose(app['paired_heat_mixed'],expected,atol=1e-23)
    assert finite_difference==pytest.approx(app['paired_heat_mixed'][0,0].real,rel=2e-6)
    assert np.linalg.norm(app['ordered_two_insertion'])>0


def test_heat_scalar_kernels_include_coincident_limit_and_infinite_tail():
    a=np.array([2.]);b=np.array([2.]);s=.3
    _,lag=_ordered_heat_lag(a,b,s)
    assert lag[0,0]==pytest.approx(.5*s*s*np.exp(-2*s),rel=2e-15)
    _,tail=_ordered_cutoff_heat_lag(a,b,s)
    assert tail[0,0]==pytest.approx(.5*np.exp(-2*s)*(s/2+1/4),rel=2e-15)
    _,unequal=_ordered_cutoff_heat_lag(a,np.array([5.]),s)
    # Independent original two-integral representation, including s=infinity.
    exact=quad(lambda t:quad(lambda x:(t-x)*np.exp(-2*(t-x)-5*x),0,t)[0]/t,
               s,np.inf,epsabs=1e-13)[0]
    assert unequal[0,0]==pytest.approx(exact,rel=2e-11)


def test_cutoff_application_is_raw_partial_and_keeps_missing_native_scope(heat_core):
    c=1/heat_core['families']['1']['n0_eigenvalues'][0]
    value=finite_eight_q_cutoff_heat_application(heat_core,c)
    expected=value['families']['1']['integrated_paired_heat_mixed']-value['families']['2']['integrated_paired_heat_mixed']
    np.testing.assert_array_equal(value['middle_minus_light_fixed_core_difference'],expected)
    assert not value['relative_overlap_subtraction_performed']
    assert not value['physical_cutoff_or_complete_native_Pauli_selected']
    with pytest.raises(ValueError,match='positive'):
        finite_eight_q_heat_application(heat_core,0)
    with pytest.raises(ValueError,match='positive'):
        finite_eight_q_cutoff_heat_application(heat_core,-1)
