import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_holomorphic_current_source import (
    holomorphic_current_stage, source_varied_unsquared_current_chain,
    compose_current_components, attach_current_chain_first,
    two_term_complex_sum,
)
from bhsm.interface.muon_continued_action_reality import _geometry, _higgs_mass_realified
from bhsm.interface.muon_holomorphic_normal_geometry import holomorphic_cap_and_weights
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_parent_maxwell_full_weak import M


def inputs():
    rng=np.random.default_rng(1238)
    raw=np.zeros(268,complex);raw[:37]=.001*rng.normal(size=37)
    raw[37:74]=.002*rng.normal(size=37);raw[74:98]=.001*rng.normal(size=24)
    raw[98:100]=[.001+.00002j,.002-.00003j]
    raw[100:260]=.002*(rng.normal(size=160)+.2j*rng.normal(size=160))
    raw[260:]=[1.1+.03j,.4-.02j,.07+.01j,.03-.01j,.02,0,0,0]
    direction=.05*(rng.normal(size=(268,2))+1j*rng.normal(size=(268,2)))
    parent=raw.copy();parent[1]+=.0004j
    refs=np.array([raw.copy(),raw.copy()]);refs[0,2]+=.0007;refs[1,3]-=.0002j
    dp=.7*direction;dr=np.stack((.2*direction,-.1j*direction))
    rep=dict(wall_trace_map=rng.normal(size=(5,4,80))*.1,rho=np.array([.08,.31,.6]))
    return raw,direction,parent,dp,refs,dr,rep


def test_joint_holomorphic_body_matches_literal_full18_and_owned_coframe():
    raw,dx,p,dp,refs,dr,rep=inputs()
    a=holomorphic_current_stage(raw,dx,p,dp,refs,dr,rep,side='child')
    g=_geometry(raw);gp,gr0,gr1=(_geometry(x)for x in (p,*refs))
    wall=np.einsum('acj,j->ac',rep['wall_trace_map'],raw[100:180])
    wall[2:]+=M*(gp['mechanical_lambda']-gr0['mechanical_lambda']+gr1['mechanical_lambda']-1)
    G=lepton_unit_trace_gauge_representation()['generators']
    h=lepton_current_hilbert_representation();space=np.einsum('ac,cij->aij',wall[2:],G)
    expected=(-1j*np.einsum('aij,ajk->ik',h['alpha'],space)+1.5*h['gamma5'])/g['R4']
    expected+=_higgs_mass_realified(raw[260:264])-1j*np.einsum('c,cij->ij',wall[0],G)/g['N']
    np.testing.assert_allclose(a['Hcan'],expected,rtol=2e-14,atol=2e-15)
    cap=holomorphic_cap_and_weights(raw[:100],points=24,response_points=24)
    np.testing.assert_allclose(a['R4'],cap['R4'].value,atol=1e-16)
    np.testing.assert_allclose(a['induced_lapse_first'],cap['N'].gradient@dx[:100],atol=1e-16)
    np.testing.assert_allclose(a['canonical_wall_current_vertices'][:4],-1j*G/g['N'],atol=2e-16)
    assert not a['source_image_projected']


def test_actual_parent_reference_higgs_and_clock_tangents_are_analytic_and_complete():
    raw,dx,p,dp,refs,dr,rep=inputs()
    a=holomorphic_current_stage(raw,dx,p,dp,refs,dr,rep,side='child')
    h=2e-5
    for k in range(2):
        values=[]
        for s in (h,-h):
            values.append(holomorphic_current_stage(raw+s*dx[:,k],dx,p+s*dp[:,k],dp,
                refs+s*dr[:,:,k],dr,rep,side='child'))
        for key in ('Hcan','total_profile','full_wall_connection'):
            fd=(values[0][key]-values[1][key])/(2*h)
            np.testing.assert_allclose(a[key+'_first'][k],fd,rtol=3e-8,atol=4e-10)
    b=holomorphic_current_stage(raw,1j*dx,p,1j*dp,refs,1j*dr,rep,side='child')
    np.testing.assert_allclose(b['Hcan_first'],1j*a['Hcan_first'],atol=4e-16)
    z=np.zeros_like(dx);zr=np.zeros_like(dr)
    held=holomorphic_current_stage(raw,dx,p,z,refs,zr,rep,side='child')
    np.testing.assert_array_equal(held['total_profile_first'],0)
    # The child's own geometric variation still enters the physical R/N.
    assert np.linalg.norm(held['Hcan_first'])>.01
    assert np.linalg.norm(a['total_profile_first'][:,0])>.001


def chain_inputs():
    rng=np.random.default_rng(873);draw=lambda shape:.12*(rng.normal(size=shape)+1j*rng.normal(size=shape))
    q,d,k,nr,nl=3,3,2,2,2
    value=dict(coordinate_steps=np.array([.06+.01j,-.025j,.04-.006j]),lapse=np.array([1+.03j,.7-.02j,1.2+.01j]),
        body=draw((q,d,d)),right_source=draw((q,d,nr)),literal_left=draw((q,nl,d)),direct_density=draw((q,nl,nr)),energy=.2+.01j)
    first={n+'_first':draw((q,k)+a.shape[1:])for n,a in value.items()if n!='energy'}
    first['energy_first']=draw((k,))
    return value,first


def independent_chain(v):
    d=v['body'].shape[-1];nr=v['right_source'].shape[-1];nl=v['literal_left'].shape[1]
    P=np.eye(d+nr+nl,dtype=complex)
    for dt,N,H,J,L,D in zip(*(v[n]for n in ('coordinate_steps','lapse','body','right_source','literal_left','direct_density'))):
        A=np.zeros_like(P);A[:d,:d]=1j*N*(v['energy']*np.eye(d)-H)
        A[:d,d:d+nr]=1j*N*J;A[d+nr:,:d]=1j*N*L;A[d+nr:,d:d+nr]=1j*N*D
        P=expm(dt*A)@P
    return dict(trace=P[:d,:d],source_return=P[:d,d:d+nr],initial_target=P[d+nr:,:d],direct_current=P[d+nr:,d:d+nr])


def test_unsquared_chain_all_clock_body_source_and_literal_dual_contacts():
    v,d=chain_inputs();a=source_varied_unsquared_current_chain(**v,**d);b=independent_chain(v)
    for key in b:np.testing.assert_allclose(a[key],b[key],atol=4e-16)
    h=2e-5
    for k in range(2):
        shift=lambda s:{n:x+s*d[n+'_first'][...,k]if n in ('coordinate_steps','lapse')else
            x+s*d[n+'_first'][:,k]if n!='energy'else x+s*d['energy_first'][k]for n,x in v.items()}
        plus,minus=independent_chain(shift(h)),independent_chain(shift(-h))
        for key in b:np.testing.assert_allclose(a[key+'_first'][k],(plus[key]-minus[key])/(2*h),rtol=4e-8,atol=1e-11)
    assert np.linalg.norm(a['trace_first'])>.005
    assert not a['analytic_left_conjugated']


def test_reset_and_forced_boundary_first_keep_every_source_and_target_contact():
    v,d=chain_inputs();a=source_varied_unsquared_current_chain(**v,**d)
    rng=np.random.default_rng(980);draw=lambda s:.1*(rng.normal(size=s)+1j*rng.normal(size=s))
    shapes={'initial_boundary':(3,3),'final_boundary':(3,3),'boundary_source':(3,2),
        'initial_target':(2,3),'final_target':(2,3),'direct_current':(2,2)}
    boundary={n:draw(s)for n,s in shapes.items()};boundary['initial_boundary']+=2*np.eye(3)
    first={n:draw((2,)+s)for n,s in shapes.items()};preserved={n:x.copy()for n,x in first.items()}
    out=attach_current_chain_first(a,boundary,first)
    for n in first:np.testing.assert_array_equal(first[n],preserved[n])
    def literal(s,k):
        z={n:boundary[n]+s*first[n][k]for n in boundary}
        b={n:a[n]+s*a[n+'_first'][k]for n in ('trace','source_return','initial_target','direct_current')}
        x=np.linalg.solve(z['initial_boundary']+z['final_boundary']@b['trace'],z['boundary_source']-z['final_boundary']@b['source_return'])
        return z['direct_current']+b['direct_current']+(z['initial_target']+b['initial_target'])@x+z['final_target']@(b['trace']@x+b['source_return'])
    h=2e-5
    for k in range(2):np.testing.assert_allclose(out['current_first'][k],(literal(h,k)-literal(-h,k))/(2*h),rtol=1e-8,atol=2e-12)
    np.testing.assert_allclose(out['current_first'],out['independent_transpose_current_first'],atol=2e-16)
    np.testing.assert_allclose(out['original_boundary_rows'],0,atol=1e-16)
    np.testing.assert_allclose(out['original_transpose_rows'],0,atol=1e-16)
    assert out['physical_mixed_derivative_not_assigned']


def test_literal_nontrivial_reset_composition_matches_direct_augmented_trace():
    v,d=chain_inputs();a=source_varied_unsquared_current_chain(**v,**d)
    b={n:np.copy(a[n])for n in ('trace','source_return','initial_target','direct_current','trace_first','source_return_first','initial_target_first','direct_current_first')}
    # A reset/source/target component uses the same original complete maps.
    b['trace']=np.diag([1.1,.8,1.03]).astype(complex);b['trace'][0,2]=.02j
    c=compose_current_components(b,a)
    def full(x):
        P=np.eye(7,dtype=complex);P[:3,:3]=x['trace'];P[:3,3:5]=x['source_return']
        P[5:,:3]=x['initial_target'];P[5:,3:5]=x['direct_current'];return P
    np.testing.assert_allclose(full(c),full(b)@full(a),atol=2e-16)
    h=1e-6
    for k in range(2):
        shifted=lambda x,s:{n:x[n]+s*x[n+'_first'][k]for n in ('trace','source_return','initial_target','direct_current')}
        fd=(full(shifted(b,h))@full(shifted(a,h))-full(shifted(b,-h))@full(shifted(a,-h)))/(2*h)
        dc={n:c[n+'_first'][k]for n in ('trace','source_return','initial_target','direct_current')}
        P=full(dc);P[3:5,3:5]=0;P[5:,5:]=0
        np.testing.assert_allclose(P,fd,atol=2e-10,rtol=1e-8)


def test_two_term_complex_sum_keeps_subulp_source_contact():
    high=np.array([1.+2j,-3.+4j]);low=np.array([2.**-60+1j*2.**-59,2.**-58-1j*2.**-57])
    h,l=two_term_complex_sum(high,low)
    np.testing.assert_array_equal(h,high)
    np.testing.assert_array_equal(l,low)
