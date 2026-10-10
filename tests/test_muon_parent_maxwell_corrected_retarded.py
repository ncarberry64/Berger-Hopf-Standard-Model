"""Independent literal-action checks on the full corrected-frame tensor."""
import numpy as np
import pytest

from bhsm.interface.muon_parent_maxwell_corrected_retarded import (
    _lift_tensor, _gauge_rows, _ad, full_constant_angular_hessian,
    constant_angular_curvatures, corrected_retarded_form, corrected_retarded_application,
    intrinsic_scalar_trace_hessian, augment_intrinsic_scalar_forms,coupled_corrected_retarded_form)
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_parent_maxwell_full_q_application import (
    retained_full_q_angular_space, full_q_reference_operators,
    apply_full_q_hessian, hessian_response_polynomials)
from bhsm.interface.muon_parent_maxwell_full_weak import M, full_maxwell_hessian_pairing
from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from bhsm.interface.muon_moving_geometric_action import retained_state
from bhsm.interface.muon_birth_candidate_geometry_action import ROOT
from bhsm.interface.muon_parent_retarded_hypercharge import WALL, regular_radial_basis


@pytest.fixture(scope='module')
def angular():
    return retained_full_q_angular_space()


def test_full_tensor_reduces_to_independently_frozen_mechanical_hessian(angular):
    q,v,m=retained_state(ROOT)
    row=geometric_connection_coefficient_jets(12,q,v,m,np.array([.61]))['rows'][0]
    A=np.zeros((5,4));At=A.copy();Ar=A.copy()
    A[2:]=M*(row['connection_lambda'].value-1)
    At[2:]=M*row['lambda_tau'].value;Ar[2:]=M*row['lambda_rho'].value
    densities=np.array([row[k].value for k in ('electric','radial','angular','electric_radial','shift')])
    local=full_constant_angular_hessian(A,At,Ar,densities)
    E=np.concatenate((np.eye(20)[None],angular['derivative_matrices']))
    products=np.array([[a.T@b for b in E] for a in E])
    actual=np.array([[_lift_tensor(local['tensor'][i,j],products) for j in range(3)] for i in range(3)])
    old=apply_full_q_hessian(row,hessian_response_polynomials(full_q_reference_operators(angular),np.eye(400)))
    np.testing.assert_allclose(actual,old,rtol=3e-14,atol=5e-8)


def test_general_temporal_radial_and_nonisotropic_spatial_fields_match_literal_action(angular):
    # CONTROL_ONLY field perturbations for an independent literal Hessian.
    q,v,m=retained_state(ROOT);c=geometric_connection_coefficient_jets(12,q,v,m,np.array([.61]))
    row=c['rows'][0];rng=np.random.default_rng(321)
    ind=rng.normal(size=(3,5,4))*.21
    total=ind.copy();total[0,2:]+=M*(row['connection_lambda'].value-1)
    total[1,2:]+=M*row['lambda_tau'].value;total[2,2:]+=M*row['lambda_rho'].value
    density=np.array([row[k].value for k in ('electric','radial','angular','electric_radial','shift')])
    local=full_constant_angular_hessian(*total,density)
    E=np.concatenate((np.eye(20)[None],angular['derivative_matrices']))
    products=np.array([[a.T@b for b in E] for a in E])
    left=rng.normal(size=(3,400));right=rng.normal(size=(3,400))
    contracted=sum(left[i]@_lift_tensor(local['tensor'][i,j],products)@right[j] for i in range(3) for j in range(3))
    def val(x):return np.einsum('pn,fn->pf',angular['basis_values'],x.reshape(20,20)).reshape(1,-1,5,4)
    def derivative(x):return np.einsum('pin,fn->pif',angular['basis_derivative_values'],x.reshape(20,20)).reshape(1,-1,3,5,4)
    fields={k:np.broadcast_to(ind[j],(1,len(angular['Haar_weights']),5,4)).copy()
            for j,k in enumerate(('gauge','gauge_tau','gauge_rho'))}
    fields['gauge_angular']=np.zeros((1,len(angular['Haar_weights']),3,5,4))
    literal=full_maxwell_hessian_pairing(c,np.ones(1),angular['Haar_weights'],**fields,
        left=val(left[0]),left_tau=val(left[1]),left_rho=val(left[2]),left_angular=derivative(left[0]),
        right=val(right[0]),right_tau=val(right[1]),right_rho=val(right[2]),right_angular=derivative(right[0]),
        geometric_derivatives=False)
    assert contracted==pytest.approx(literal['value'],rel=3e-13,abs=1e-6)
    assert np.linalg.norm(local['curvatures']['Ftr'])>0
    assert np.linalg.norm(local['curvature_contact'])>0


@pytest.mark.parametrize('bad',[None,np.zeros((4,4)),np.full((5,4),np.nan)])
def test_missing_full_connection_does_not_default_to_zero(bad):
    with pytest.raises((ValueError,TypeError)):
        constant_angular_curvatures(bad,np.zeros((5,4)),np.zeros((5,4)))


@pytest.fixture(scope='module')
def corrected():
    f=coupled_corrected_retarded_form(time_nodes=5,radial_points=12)
    return f,corrected_retarded_application(f,time_steps=48)


def test_exact_corrected_coefficient_vector_and_unprojected_defect_are_retained(corrected):
    f,r=corrected
    assert f['corrected_coefficients'].shape==(130,)
    assert f['full_background_values'].shape==(5,3,12,5,4)
    assert f['iterate_receipt']['updated_constraint_density_max']>.3
    assert f['minimum_interior_mass_eigenvalue']>0
    assert r['Gauss_residual_maximum_relative']<3e-14
    assert r['action_boundary_relative_defect']<2e-9
    assert r['adjoint_pairing_maximum_defect']<3e-7
    assert r['physical_gauge_quotient_closed'] is False
    assert r['native_heat_evaluated'] is False
    assert r['physical_Pauli_form'] is None
    assert np.linalg.norm(r['paired_gauge_Euler_reaction'])>0
    assert r['state'].shape[1:]==(800,8)
    assert np.linalg.norm(r['intrinsic_H_response'])>0
    assert np.linalg.norm(r['intrinsic_H_canonical_momenta'])>0
    assert np.linalg.norm(r['intrinsic_scalar_wall_current_pairing'])>0
    assert f['nu_squared_action_member']==4.
    assert f['scalar_Maxwell_relative_normalization']==8.


def test_corrected_added_gradient_rows_match_literal_action_including_At_Ar(corrected):
    # CONTROL_ONLY finite test vectors.  The background is the complete
    # recorded corrected iterate; all eta jets derive from that connection.
    f,_=corrected;a=f['angular'];index=2
    q=f['corrected_geometry'][index,:37];v=f['corrected_geometry'][index,37:74]
    m=f['corrected_geometry'][index,74:98];s,sr=f['corrected_geometry'][index,98:]
    c=geometric_connection_coefficient_jets(12,q,v,m,f['rho'],source_value=s,source_rate=sr)
    A,At,Ar=f['full_background_values'][index]
    eta=np.eye(80)[:,17];rate=.4;I=np.eye(20)
    z=np.zeros(488);z[:400]=.2*a['source_coefficients'][:,2];z[13]=.3;z[91]=-.1;z[480]=.7
    dz=.23*z;dz[:80]=0
    p2=[]
    for rho,(p,l),(pr,lr) in zip(f['rho'],f['H'],f['Hr']):
        from bhsm.interface.muon_parent_retarded_hypercharge import ALPHA
        x=rho/WALL;normal=p/(x**ALPHA*(1-x))
        p2.append(normal/WALL**2*(ALPHA*(ALPHA-1)*x**(ALPHA-2)*(1-x)-2*ALPHA*x**(ALPHA-1)))
    left=[];lt=[];lr=[];right=[];rt=[];rr=[]
    for j in range(len(A)):
        p,l=f['H'][j];pr,dr=f['Hr'][j]
        ad=[np.kron(_ad(x),I) for x in A[j]]
        adt=[np.kron(_ad(x),I) for x in At[j]]
        adr=[np.kron(_ad(x),I) for x in Ar[j]]
        D=[np.kron(np.eye(4),E)+ad[2+i] for i,E in enumerate(a['derivative_matrices'])]
        L=np.concatenate((p*(ad[0]@eta+rate*eta),pr*eta+p*(ad[1]@eta),*(p*(d@eta) for d in D)))
        Lt=np.concatenate((p*(adt[0]@eta+rate*(ad[0]@eta)),pr*rate*eta+p*(adt[1]@eta+rate*(ad[1]@eta)),
            *(p*(adt[2+i]@eta+rate*(D[i]@eta)) for i in range(3))))
        Lr=np.concatenate((pr*(ad[0]@eta+rate*eta)+p*(adr[0]@eta),p2[j]*eta+pr*(ad[1]@eta)+p*(adr[1]@eta),
            *(pr*(D[i]@eta)+p*(adr[2+i]@eta) for i in range(3))))
        Q=a['source_coefficients']
        left.append(L);lt.append(Lt);lr.append(Lr)
        right.append(p*z[:400]+l*(Q@z[480:]));rt.append(p*dz[:400]+l*(Q@dz[480:]));rr.append(pr*z[:400]+dr*(Q@z[480:]))
    def val(x):return np.einsum('pn,rfn->rpf',a['basis_values'],np.asarray(x).reshape(-1,20,20)).reshape(len(A),-1,5,4)
    def ev(x):return np.einsum('pin,rfn->rpif',a['basis_derivative_values'],np.asarray(x).reshape(-1,20,20)).reshape(len(A),-1,3,5,4)
    fields=[]
    for j,row in enumerate(c['rows']):
        ind=np.array([A[j],At[j],Ar[j]])
        ind[0,2:]-=M*(row['connection_lambda'].value-1)
        ind[1,2:]-=M*row['lambda_tau'].value;ind[2,2:]-=M*row['lambda_rho'].value
        fields.append(ind)
    fields=np.array(fields)
    given={k:np.repeat(fields[:,j,None],len(a['Haar_weights']),axis=1)
           for j,k in enumerate(('gauge','gauge_tau','gauge_rho'))}
    given['gauge_angular']=np.zeros_like(ev(left))
    literal=full_maxwell_hessian_pairing(c,f['quadrature'],a['Haar_weights'],**given,
        left=val(left),left_tau=val(lt),left_rho=val(lr),left_angular=ev(left),
        right=val(right),right_tau=val(rt),right_rho=val(rr),right_angular=ev(right),geometric_derivatives=False)
    G0z,G0v,G1z,G1v=f['gauge_weak_rows'](f['time_nodes'][index])
    applied=eta@(G0z@z+G0v@dz+rate*(G1z@z+G1v@dz))
    assert applied==pytest.approx(literal['value'],rel=3e-12,abs=3e-7)


def test_intrinsic_real_scalar_full_hessian_includes_gauge_H_mixed_contacts(angular):
    # CONTROL_ONLY complete fields/directions.  Literal polynomial action
    # is evaluated in physical Haar measure, independently of the matrix.
    H=np.array([.2,.7,-.1,.15]);Ht=np.array([.1,-.03,.02,.08])
    A=np.arange(20).reshape(5,4)*.017-.12;wt,ws,wv=1.2,.7,.9
    lam,nu=.13,4.;rng=np.random.default_rng(763)
    left=rng.normal(size=560)*.13;right=rng.normal(size=560)*.13
    local=intrinsic_scalar_trace_hessian(H,Ht,A,np.array([wt,ws,wv]),lambda_H=lam,nu_squared_action=nu,angular=angular)
    V=angular['basis_values'];E=angular['basis_derivative_values'];T=higgs_u2_real_representation()['real_generators']
    def field(x):
        h=H+V@x[:80].reshape(4,20).T
        ht=Ht+V@x[480:].reshape(4,20).T
        a=A+np.einsum('pn,fcn->pfc',V,x[80:480].reshape(5,4,20))
        dh=np.einsum('pin,cn->pic',E,x[:80].reshape(4,20))
        covt=ht+np.einsum('pc,cij,pj->pi',a[:,0],T,h)
        cov=dh+np.einsum('pac,cij,pj->pai',a[:,2:],T,h)
        density=wt*np.sum(covt*covt,axis=1)-ws*np.sum(cov*cov,axis=(1,2))-wv*lam*(np.sum(h*h,axis=1)-nu)**2
        return 2*np.pi**2*(angular['Haar_weights']@density)
    def mixed(step):
        return (field(step*(left+right))-field(step*(left-right))-field(step*(-left+right))+field(-step*(left+right)))/(4*step*step)
    # Quartic scalar action makes this two-radius coefficient extraction
    # exact in algebra, rather than relying on infinitesimal truncation.
    literal=(4*mixed(.125)-mixed(.25))/3
    assert left@local['matrix']@right==pytest.approx(literal,rel=2e-12,abs=2e-10)
    assert np.linalg.norm(local['matrix'][:80,80:480])>0
    assert local['extra_wall_advection_count']==0
    np.testing.assert_array_equal(local['matrix'][160:240],np.zeros((80,560)))


def test_intrinsic_unknown_potential_cannot_be_filled_and_known_parameter_is_consumed(angular):
    args=dict(H=np.array([0.,1.,0.,0.]),H_tau=np.zeros(4),gauge_trace=np.zeros((5,4)),
        metric_weights=np.ones(3),lambda_H=.13,angular=angular)
    with pytest.raises((ValueError,TypeError)):
        intrinsic_scalar_trace_hessian(**args,nu_squared_action=None)
    low=intrinsic_scalar_trace_hessian(**args,nu_squared_action=0.)
    high=intrinsic_scalar_trace_hessian(**args,nu_squared_action=4.)
    np.testing.assert_allclose(high['matrix'][:80,:80]-low['matrix'][:80,:80],4*low['nu_squared_coefficient'],atol=3e-14)


def test_intrinsic_extension_is_one_literal_action_with_source_and_momenta(angular):
    # CONTROL_ONLY coefficient vectors, independent of the retarded solve.
    rng=np.random.default_rng(823);H=np.array([0.,1.,0.,0.]);Ht=np.zeros(4);A=np.zeros((5,4))
    S=intrinsic_scalar_trace_hessian(H,Ht,A,np.ones(3),lambda_H=.13,nu_squared_action=4.,angular=angular)['matrix']
    zero=np.zeros((408,408));Q=angular['source_coefficients']
    mass,mixed,stiffness=augment_intrinsic_scalar_forms((zero,zero,zero),S,Q)
    z=rng.normal(size=488)*.1;v=rng.normal(size=488)*.1
    direct=np.r_[z[400:480],Q@z[480:],v[400:480]]
    assert .5*v@mass@v+z@mixed@v+.5*z@stiffness@z==pytest.approx(4*direct@S@direct,rel=2e-14)
    assert np.linalg.norm(stiffness[400:480,480:])>0
    assert np.linalg.eigvalsh(mass[400:480,400:480])[0]>0
    np.testing.assert_array_equal(mass[:80],np.zeros((80,488)))


def test_linear_geometry_reduction_requires_this_homogeneous_even_background(angular):
    assert np.max(abs(angular['Haar_weights']@angular['basis_values']))<1e-14
    means=np.einsum('p,pin->in',angular['Haar_weights'],angular['basis_derivative_values'])
    assert np.max(abs(means))<2e-14
    # A nonconstant odd background creates even pairings; this test rules
    # out interpreting the linear parity reduction as nonlinear closure.
    phi=angular['basis_values'][:,0]
    assert angular['Haar_weights']@(phi*phi)==pytest.approx(1.,abs=2e-14)


def test_scalar_tensor_matches_material_backend_and_does_not_readvect_Ar(angular):
    from bhsm.interface.muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
    from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
    # CONTROL_ONLY backend interoperability.  Two coefficient directions
    # share value/ordinary derivative/gauge maps; no independent DH input.
    rng=np.random.default_rng(442);H=np.array([.1,.8,-.2,.03]);Ht=np.array([.1,0.,.2,.04])
    A=rng.normal(size=(5,4))*.17;left=rng.normal(size=560)*.1;right=rng.normal(size=560)*.1
    weights={'wT':Jet.constant(1.2,0),'wS':Jet.constant(.7,0),'wV':Jet.constant(.9,0),
        'wall_rate':Jet.constant(.37,0),'mechanical_connection_lambda':Jet.constant(1.,0)}
    count=len(angular['Haar_weights']);V=angular['basis_values'];E=angular['basis_derivative_values']
    value=np.zeros((count,4,10));value[:,:,:4]=np.eye(4)
    ordinary=np.zeros((count,4,4,10));ordinary[:,0,:,4:8]=np.eye(4)
    gauge=np.zeros((count,5,4,22));gauge[:,:,:,:20]=np.eye(20).reshape(5,4,20)
    for j,direction in enumerate((left,right)):
        value[:,:,8+j]=V@direction[:80].reshape(4,20).T
        ordinary[:,0,:,8+j]=V@direction[480:].reshape(4,20).T
        ordinary[:,1:,:,8+j]=np.einsum('pin,cn->pic',E,direction[:80].reshape(4,20))
        gauge[:,:,:,20+j]=np.einsum('pn,fcn->pfc',V,direction[80:480].reshape(5,4,20))
    result=material_intrinsic_higgs_gauge_action_jet(weights,
        scalar_coefficients=np.r_[H,Ht,0.,0.],scalar_value_map=value,scalar_derivative_map=ordinary,
        gauge_coefficients=np.r_[A.ravel(),0.,0.],gauge_trace_map=gauge,
        angular_quadrature=angular['Haar_weights'],lambda_H=.13,nu_squared_action=4.)
    hessian=result['action'].hessian
    reference=hessian[8,9]+hessian[8,31]+hessian[30,9]+hessian[30,31]
    tensor=intrinsic_scalar_trace_hessian(H,Ht,A,np.array([1.2,.7,.9]),lambda_H=.13,nu_squared_action=4.,angular=angular)
    assert left@tensor['matrix']@right==pytest.approx(reference,rel=3e-13,abs=2e-11)
    assert result['physical_wall_rate'].value==.37
    assert result['extra_reference_trace_advection_count']==0


def test_complex_connection_cannot_be_silently_discarded():
    bad=np.zeros((5,4),complex);bad[0,1]=1j
    with pytest.raises(ValueError,match='no complex'):
        constant_angular_curvatures(bad,np.zeros((5,4)),np.zeros((5,4)))


def test_complete_response_operator_archives_are_lossless_and_deterministic(tmp_path):
    from bhsm.interface.muon_parent_maxwell_corrected_retarded import _write_array_archives
    # Packaging control: no selected physical field or solver data invented.
    response={'state':np.arange(48,dtype=float).reshape(2,3,8),'complex_adjoint':np.array([1+2j])}
    operator={'unreduced_action_K':np.eye(6),'coordinate_labels':np.arange(6,dtype=np.int64)}
    receipts=[]
    for name in ('one','two'):
        directory=tmp_path/name;directory.mkdir()
        receipts.append(_write_array_archives(directory,response,operator))
        seen=set()
        for filename,original in (('application.npz',response),('operator.npz',operator)):
            with np.load(directory/filename) as data:
                assert set(data.files)==set(original)
                seen.update(data.files)
                for key in original:
                    assert data[key].dtype==original[key].dtype
                    np.testing.assert_array_equal(data[key],original[key])
        assert seen==set(response)|set(operator)
    assert receipts[0]==receipts[1]
    for name in receipts[0]:
        assert (tmp_path/'one'/name).read_bytes()==(tmp_path/'two'/name).read_bytes()
    with pytest.raises(ValueError,match='disjoint'):
        _write_array_archives(tmp_path,{'duplicate':np.zeros(1)},{'duplicate':np.ones(1)})
