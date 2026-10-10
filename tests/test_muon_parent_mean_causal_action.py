"""Actual finite-action interoperability; synthetic directions are CONTROL_ONLY.

These tests neither choose a physical H trace nor solve a causal problem.
The independent field-action formula retains every five-component curvature
and the intrinsic material scalar pairing, including its charged Gauss row.
"""
import numpy as np
import pytest

from bhsm.interface import muon_parent_mean_causal_action as mean
from bhsm.interface.muon_birth_coupled_constraint_retraction import pointwise_assigned_action
from bhsm.interface.muon_parent_gauge_geometry_correction import finite_common_iterate_at_time, compact_temporal_basis
from bhsm.interface.muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER, M
from bhsm.interface.muon_parent_retarded_hypercharge import WALL, regular_radial_basis


@pytest.fixture(scope='module')
def actual():
    family=mean.mean_action_family()
    u=family['length']/8
    result=mean.local_mean_action(u,family)
    rep=family['representation'];c=family['coefficients'];t=u-family['length']
    data=finite_common_iterate_at_time(t,c,rep,family['reference'])
    wall=finite_common_iterate_at_time(t,c,rep,family['reference'],rho=np.array([WALL]))
    b,bt=compact_temporal_basis(np.array([t]),rep['length']);sc=c[rep['scalar_start']:]
    H=b[0]*sc[:4]+sc[4:];Ht=bt[0]*sc[:4]
    return family,result,data,wall,H,Ht


def test_coordinate_lift_preserves_all_components_and_excludes_At_rate(actual):
    family,*_=actual;labels=family['representation']['gauge_labels']
    coords=mean.mean_coordinate_lift(labels);P=coords['lift']
    # Independent random master vector: every represented value/rate must
    # reach its literal action coordinate without a second copy of At.
    z=np.random.default_rng(112).normal(size=216);raw=P@z
    np.testing.assert_array_equal(raw[:37],z[:37])
    np.testing.assert_array_equal(raw[37:74],z[90:127])
    np.testing.assert_array_equal(raw[74:98],z[180:204])
    assert raw[98]==z[37] and raw[99]==z[127]
    di=ai=0
    for i,label in enumerate(labels):
        if label['field']=='A_tau':
            assert raw[100+i]==z[204+ai] and raw[160+i]==0
            ai+=1
        else:
            assert raw[100+i]==z[38+di] and raw[160+i]==z[128+di]
            di+=1
    assert (di,ai)==(48,12)
    np.testing.assert_array_equal(raw[220:224],z[86:90])
    np.testing.assert_array_equal(raw[224:228],z[176:180])
    np.testing.assert_array_equal(P.T@P,np.eye(216))


def test_incomplete_gauge_decomposition_is_rejected(actual):
    labels=actual[0]['representation']['gauge_labels']
    with pytest.raises(ValueError,match='all60'):
        mean.mean_coordinate_lift(labels[:-1])
    bad=[dict(x,field='A_rho') for x in labels]
    with pytest.raises(ValueError,match='all5'):
        mean.mean_coordinate_lift(bad)


def test_literal_assigned_action_matches_geometry_blocks_and_constraints(actual):
    family,result,data,wall,H,Ht=actual;rep=family['representation']
    independent=pointwise_assigned_action(data['q'],data['qdot'],data['m'],
        rho=rep['rho'],radial_quadrature=rep['radial_quadrature'],fields=data['fields'],
        H_real=H,H_rate=Ht,wall_gauge=wall['fields']['gauge'][0,0],
        lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.,surface_gamma=None,
        normal=data['normal'],normal_rate=data['normal_rate'],cap_points=rep['cap_points'])
    assert result['value']==pytest.approx(independent['value'],rel=2e-15)
    np.testing.assert_allclose(result['raw_gradient'][:100],independent['gradient'],rtol=3e-14,atol=2e-12)
    np.testing.assert_allclose(result['raw_hessian'][:100,:100],independent['hessian'],rtol=3e-13,atol=2e-11)
    np.testing.assert_allclose(result['constraint_base'][:24],independent['multiplier_constraints'],rtol=3e-14,atol=2e-12)
    # A projected correction is not a stationary background.  These are
    # actual nonzero same-action multiplier values, not missing data.
    assert np.linalg.norm(result['constraint_base'])>.3
    assert result['stationary_background'] is False
    assert result['physical_two_arm_domain_selected'] is False
    assert result['metric_chart']=='materialAt_ref once'
    assert result['conditional_nu_squared_action']==4.
    assert result['surface_gamma'] is None


def _bracket(a,b):
    value=np.zeros(np.broadcast_shapes(a.shape,b.shape))
    value[...,:3]=np.cross(a[...,:3],b[...,:3])/np.sqrt(2)
    return value


def _literal_field_action(actual,direction,s):
    """One independent polynomial in supplied CONTROL_ONLY field direction."""
    family,_,data,_,H,Ht=actual;rep=family['representation'];fields=data['fields']
    geo=geometric_connection_coefficient_jets(12,data['q'],data['qdot'],data['m'],rep['rho'],
        source_value=data['normal'],source_rate=data['normal_rate'])
    # Add the mechanical connection exactly once.  All chart coefficients
    # are evaluated from the same q/qdot/m, including lambda_tau.
    a=fields['gauge'][:,0].copy();at=fields['gauge_tau'][:,0].copy();ar=fields['gauge_rho'][:,0].copy()
    a+=s*np.einsum('rjpic,j->rpic',rep['gauge_basis'],direction[100:160])[:,0]
    at+=s*np.einsum('rjpic,j->rpic',rep['gauge_basis'],direction[160:220])[:,0]
    ar+=s*np.einsum('rjpic,j->rpic',rep['gauge_radial_basis'],direction[100:160])[:,0]
    for i,row in enumerate(geo['rows']):
        a[i,2:]+=(row['connection_lambda'].value-1)*M
        at[i,2:]+=row['lambda_tau'].value*M
        ar[i,2:]+=row['lambda_rho'].value*M
    X=at[:,1]-ar[:,0]+_bracket(a[:,0],a[:,1])
    Ft=at[:,2:]+_bracket(a[:,0,None],a[:,2:])
    Fr=ar[:,2:]+_bracket(a[:,1,None],a[:,2:])
    B=2*a[:,2:].copy()
    for i,j,k in ((0,1,2),(1,2,0),(2,0,1)):
        B[:,i]+=_bracket(a[:,j+2],a[:,k+2])
    e,r,d,k,beta=(np.array([row[key].value for row in geo['rows']])
                    for key in ('electric','radial','angular','electric_radial','shift'))
    maxwell=.5*(rep['radial_quadrature']@(k*np.sum(X*X,axis=1)
        +e*np.sum((Ft-beta[:,None,None]*Fr)**2,axis=(1,2))
        -r*np.sum(Fr*Fr,axis=(1,2))-d*np.sum(B*B,axis=(1,2))))
    # Baseline subtraction is independent of the field direction and
    # therefore cannot affect its first/second polynomial coefficients.
    h=H+s*direction[220:224];ht=Ht+s*direction[224:228]
    wb,_=regular_radial_basis(np.array([WALL]),rep['radial_order'])
    trace=np.zeros((5,4))
    for i,label in enumerate(rep['gauge_labels']):
        trace[FIELD_ORDER.index(label['field']),label['internal']]+=wb[0,label['radial']]*(
            s*direction[100+i])
    wall=finite_common_iterate_at_time(result_time(actual),family['coefficients'],rep,family['reference'],rho=np.array([WALL]))
    trace+=wall['fields']['gauge'][0,0]
    weights=intrinsic_m4_weight_jet(12,data['q'],data['qdot'],data['m'],
        source_value=data['normal'],source_rate=data['normal_rate'])
    trace[2:]+=(weights['mechanical_connection_lambda'].value-1)*M
    generators=higgs_u2_real_representation()['real_generators']
    connection=np.einsum('fc,cij->fij',trace[[0,2,3,4]],generators)
    DH=np.einsum('fij,j->fi',connection,h);DH[0]+=ht
    scalar=(weights['wT'].value*(DH[0]@DH[0])-weights['wS'].value*np.sum(DH[1:]**2)
        -weights['wV'].value*rep['scalar_matching']['lambda_H']*(h@h-4.)**2)/mean.VOLUME
    return mean.MAXWELL_TO_CAP*maxwell+scalar


def result_time(actual):return actual[1]['represented_coefficient_time']


@pytest.mark.parametrize('kind',['H_radial','At_H','Ar_nonabelian','mixed_values_rates'])
def test_field_gradient_and_hessian_equal_literal_quartic_coefficients(actual,kind):
    family,result,*_=actual;labels=family['representation']['gauge_labels'];direction=np.zeros(228)
    if kind=='H_radial':direction[221]=.17
    elif kind=='At_H':
        direction[220:224]=[.03,.11,-.07,.09]
        direction[100+next(i for i,x in enumerate(labels) if x['wall_lift'] and x['field']=='A_tau' and x['internal']==3)]=.15
    elif kind=='Ar_nonabelian':
        for field,c in (('A_tau',0),('A_rho',1),('A_2',2)):
            direction[100+next(i for i,x in enumerate(labels) if x['radial']==0 and x['field']==field and x['internal']==c)]=.13
    else:
        rng=np.random.default_rng(43);direction[100:228]=rng.normal(size=128)*.03
        direction[160+family['coordinates']['At_indices']]=0
    # A degree-four action is reconstructed exactly at five numerical
    # nodes; this is not a small-step Hessian mirror of the implementation.
    nodes=np.array([-2.,-1.,0.,1.,2.]);values=np.array([_literal_field_action(actual,direction,s) for s in nodes])
    coefficients=np.linalg.solve(np.vander(nodes,5,increasing=True),values)
    assert direction@result['raw_gradient']==pytest.approx(coefficients[1],rel=3e-10,abs=3e-11)
    assert direction@result['raw_hessian']@direction==pytest.approx(2*coefficients[2],rel=4e-10,abs=3e-11)


def test_actual_mean_load_is_all64_pairs_in_the_same_cap_normalization(actual):
    family,result,*_=actual
    with np.load(family['root']/family['source_application']/'application.npz') as f:
        raw=np.concatenate((f['combined_geometry_100'],f['combined_mean_gauge_value'].reshape(17,60,8,8),
            f['combined_mean_gauge_time'].reshape(17,60,8,8),f['scalar_mean_H_value'],f['scalar_mean_H_time']),axis=1)
    expected=mean.MAXWELL_TO_CAP*np.einsum('ji,tjAB->tiAB',family['coordinates']['lift'],raw)
    np.testing.assert_array_equal(family['source_values'],expected)
    np.testing.assert_allclose(result['Jx'],expected[2,:90],rtol=0,atol=0)
    assert np.linalg.norm(result['Jy'][:24])>1e8
    assert np.linalg.norm(result['Jx'][86:90])>0
    np.testing.assert_allclose(expected,expected.swapaxes(-1,-2),rtol=2e-15,atol=1e-5)


@pytest.mark.parametrize('with_gauge',[False,True])
def test_geometry_field_cross_is_literal_action_gradient_derivative(actual,with_gauge):
    family,result,data,wall,H,Ht=actual;rep=family['representation']
    direction=np.zeros(228);direction[220:228]=[.03,.11,-.07,.09,.02,-.05,.04,.01]
    if with_gauge:
        rng=np.random.default_rng(775);direction[100:220]=rng.normal(size=120)*.08
        direction[160+family['coordinates']['At_indices']]=0
    wallbasis,_=regular_radial_basis(np.array([WALL]),rep['radial_order'])
    dwall=np.zeros((5,4))
    for i,label in enumerate(rep['gauge_labels']):
        dwall[FIELD_ORDER.index(label['field']),label['internal']]+=wallbasis[0,label['radial']]*direction[100+i]
    def gradient(s):
        fields={k:x.copy() for k,x in data['fields'].items()}
        fields['gauge']+=s*np.einsum('rjpic,j->rpic',rep['gauge_basis'],direction[100:160])
        fields['gauge_tau']+=s*np.einsum('rjpic,j->rpic',rep['gauge_basis'],direction[160:220])
        fields['gauge_rho']+=s*np.einsum('rjpic,j->rpic',rep['gauge_radial_basis'],direction[100:160])
        applied=pointwise_assigned_action(data['q'],data['qdot'],data['m'],rho=rep['rho'],
            radial_quadrature=rep['radial_quadrature'],fields=fields,
            H_real=H+s*direction[220:224],H_rate=Ht+s*direction[224:228],
            wall_gauge=wall['fields']['gauge'][0,0]+s*dwall,
            lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=4.,surface_gamma=None,
            normal=data['normal'],normal_rate=data['normal_rate'],cap_points=rep['cap_points'])
        # Remove the unperturbed cap before differencing.  Its large value
        # cannot swamp the independent geometry/charged-matter contacts.
        return sum(applied['sectors'][k]['gradient'] for k in ('independent_Maxwell','Higgs_assigned'))
    derivative=(gradient(-2)-8*gradient(-1)+8*gradient(1)-gradient(2))/12
    np.testing.assert_allclose(result['raw_hessian'][:100]@direction,derivative,rtol=3e-11,atol=5e-11)
    assert np.linalg.norm(derivative[74:98])>0  # lapse/shift constraint cross
    assert np.linalg.norm(derivative[98:])>0   # reached normal/rate cross


def test_affine_trace_restriction_retains_all20_reactions(actual,monkeypatch):
    family,result,*_=actual
    # Repeated actual local data exercise the boundary-index map only;
    # they are not a time-interpolated physical solution.
    monkeypatch.setattr(mean,'local_mean_action',lambda t,f:result)
    samples=mean.retained_mean_action_family(time_nodes=3)
    assert (samples['x_count'],samples['v_count'],samples['y_count'])==(74,74,32)
    np.testing.assert_array_equal(samples['H_real_indices'],[70,71,72,73])
    labels=family['representation']['gauge_labels'];coords=family['coordinates']
    wallx=[38+j for j,i in enumerate(coords['dynamic_gauge_indices']) if labels[i]['wall_lift']]
    wally=[204+j for j,i in enumerate(coords['At_indices']) if labels[i]['wall_lift']]
    np.testing.assert_array_equal(samples['rejected_wall_value_rows'],wallx+wally)
    assert len(set(wallx+wally))==20
    Q=samples['lift_to_full_mean'];np.testing.assert_array_equal(Q.T@Q,np.eye(180))
    np.testing.assert_array_equal(Q[samples['rejected_wall_value_rows']],0)
    np.testing.assert_array_equal(samples['full_source_samples'][0],np.concatenate((result['Jx'],result['Jv'],result['Jy'])))
    assert np.linalg.norm(samples['full_source_samples'][0,samples['rejected_wall_value_rows']])>0
    assert samples['physical_gauge_quotient_closed'] is False
    assert samples['native_heat_or_Pauli_evaluated'] is False


def test_no_time_extrapolation_or_insufficient_temporal_sample(actual):
    family,*_=actual
    for t in (-1e-9,family['length']+1e-9,float('nan')):
        with pytest.raises(ValueError,match='outside'):
            mean.local_mean_action(t,family)
    with pytest.raises(ValueError,match='at least3'):
        mean.retained_mean_action_family(time_nodes=2)
