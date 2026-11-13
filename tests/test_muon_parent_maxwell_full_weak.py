"""Literal full-action and off-shell Ward tests; synthetic data are CONTROL_ONLY."""
import numpy as np
import pytest

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_matched_mechanical_source import epsilon
from bhsm.interface.muon_parent_maxwell_full_weak import (
    M, full_maxwell_action_jet, full_maxwell_weak_geometric_jets,
    full_maxwell_hessian_pairing, retained_full_background_application,
    full_maxwell_gauge_hessian_matrix,
    background_subtracted_maxwell_action_jet,
)
from bhsm.interface.muon_parent_maxwell_geometry_weak import spatial_maxwell_weak_geometric_jets


def geometry(x=0., y=0.):
    # Explicit two-dimensional geometry control, not an E1 physical state.
    x = Jet.affine(x, np.array([1., 0.])); y = Jet.affine(y, np.array([0., 1.]))
    e, r, d = 2*x.exp(), 3*y.exp(), 4*(-x-y).exp()
    row = dict(electric=e, radial=r, angular=d, electric_radial=e*r/d,
        shift=.3+x-.4*y, connection_lambda=.7+.04*x,
        lambda_tau=.12+.3*y, lambda_rho=-.2+x*y)
    return dict(rows=[row], coordinate_count=2, clock='CONTROL_ONLY_coordinate_time')


def fields(seed):
    rng = np.random.default_rng(seed)
    return dict(gauge=.2*rng.normal(size=(1, 3, 5, 4)),
        gauge_tau=.3*rng.normal(size=(1, 3, 5, 4)),
        gauge_rho=.3*rng.normal(size=(1, 3, 5, 4)),
        gauge_angular=.2*rng.normal(size=(1, 3, 3, 5, 4)))


def indexed(d):
    return {k.replace('gauge', 'tests'):v[:, None] for k,v in d.items()}


def shifted(a, d, h):
    return {k:a[k]+h*d[k] for k in a}


def bracket(a, b):
    out = np.zeros(np.broadcast_shapes(a.shape, b.shape))
    out[..., :3] = np.cross(a[..., :3], b[..., :3])/np.sqrt(2)
    return out


def literal_action(c, field):
    # Direct five-component curvature action, independent of the producer's
    # lambda-polynomial expansion and all exported weak/Hessian functions.
    row = c['rows'][0]; a, at, ar, ea = (field[k][0].copy() for k in
        ('gauge','gauge_tau','gauge_rho','gauge_angular'))
    lam, lt, lr = (row[k].value for k in ('connection_lambda','lambda_tau','lambda_rho'))
    a[:, 2:] += (lam-1)*M; at[:, 2:] += lt*M; ar[:, 2:] += lr*M
    X = at[:, 1]-ar[:, 0]+bracket(a[:, 0], a[:, 1])
    Ft = at[:, 2:]-ea[:, :, 0]+bracket(a[:, 0, None], a[:, 2:])
    Fr = ar[:, 2:]-ea[:, :, 1]+bracket(a[:, 1, None], a[:, 2:])
    B = 2*a[:, 2:]
    eps = epsilon()
    for i in range(3):
        for j in range(3):
            for k in range(3):
                B[:, i] += eps[i,j,k]*(ea[:, j,k+2]+.5*bracket(a[:, j+2],a[:, k+2]))
    e, r, d, k, beta = (row[key].value for key in ('electric','radial','angular','electric_radial','shift'))
    return .5*np.mean(k*np.sum(X*X,axis=-1)
        +e*np.sum((Ft-beta*Fr)**2,axis=(-1,-2))-r*np.sum(Fr*Fr,axis=(-1,-2))
        -d*np.sum(B*B,axis=(-1,-2)))


def hessian(c, a, v, z, **options):
    dirs = {k.replace('gauge','left'):x for k,x in v.items()}
    dirs.update({k.replace('gauge','right'):x for k,x in z.items()})
    return full_maxwell_hessian_pairing(c, [1.], np.ones(3)/3, **a, **dirs, **options)


def test_nonzero_temporal_radial_full_action_and_weak_are_the_same_scalar_variation():
    a, v = fields(1), fields(2); c=geometry()
    action = full_maxwell_action_jet(c, [1.], np.ones(3)/3, **a)
    assert action['value'] == pytest.approx(literal_action(c,a), rel=2e-15)
    weak = full_maxwell_weak_geometric_jets(c, [1.], np.ones(3)/3, **a, **indexed(v))
    h=2e-6
    derivative=(literal_action(c,shifted(a,v,h))-literal_action(c,shifted(a,v,-h)))/(2*h)
    assert weak['weak']['values'][0] == pytest.approx(derivative, rel=2e-8, abs=1e-8)
    assert not weak['unforced_Gauss_imposed']
    assert not weak['event_contacts_appended']


def test_background_subtraction_removes_owned_geometry_energy_but_preserves_gauge_variation():
    c=geometry();a=fields(15);v=fields(16);hw=np.ones(3)/3
    zero={k:np.zeros_like(x) for k,x in a.items()}
    reference=background_subtracted_maxwell_action_jet(c,[1.],hw,**zero)
    assert reference['value']==0
    np.testing.assert_array_equal(reference['gradient'],0)
    np.testing.assert_array_equal(reference['hessian'],0)
    assert abs(reference['mechanical_reference_value'])>1
    assert not reference['background_energy_added_twice']
    h=1e-6
    plus=background_subtracted_maxwell_action_jet(c,[1.],hw,**shifted(a,v,h))['value']
    minus=background_subtracted_maxwell_action_jet(c,[1.],hw,**shifted(a,v,-h))['value']
    weak=full_maxwell_weak_geometric_jets(c,[1.],hw,**a,**indexed(v))['weak']['values'][0]
    assert (plus-minus)/(2*h)==pytest.approx(weak,rel=2e-8,abs=1e-8)


def test_full_nonlinear_hessian_retains_ftr_and_magnetic_mixed_contacts():
    a,v,z=fields(3),fields(4),fields(5);c=geometry()
    result=hessian(c,a,v,z)
    fast=hessian(c,a,v,z,geometric_derivatives=False)
    assert result['value']==pytest.approx(fast['value'], rel=2e-15, abs=2e-14)
    assert result['value']==pytest.approx(hessian(c,a,z,v)['value'], rel=2e-15)
    h=2e-4
    at=lambda x,y:shifted(shifted(a,v,x),z,y)
    fd=(literal_action(c,at(h,h))-literal_action(c,at(h,-h))
        -literal_action(c,at(-h,h))+literal_action(c,at(-h,-h)))/(4*h*h)
    assert result['value']==pytest.approx(fd, rel=3e-7, abs=2e-7)
    assert abs(result['curvature_contact'])>.01
    assert fast['gradient'] is None and fast['hessian'] is None


def test_batched_same_action_hessian_matches_pairings_including_all_gauss_fields():
    c=geometry();a=fields(11);directions=[fields(12),fields(13),fields(14)]
    tests={k.replace('gauge','tests'):np.stack([d[k] for d in directions],axis=1) for k in a}
    result=full_maxwell_gauge_hessian_matrix(c,[1.],np.ones(3)/3,**a,**tests)
    for i,left in enumerate(directions):
        for j,right in enumerate(directions):
            exact=hessian(c,a,left,right,geometric_derivatives=False)
            assert result['matrix'][i,j]==pytest.approx(exact['value'],rel=3e-15,abs=5e-14)
            assert result['curvature_contact_matrix'][i,j]==pytest.approx(exact['curvature_contact'],rel=3e-15,abs=5e-14)
    assert result['symmetry_defect']<1e-14
    assert not result['temporal_radial_Gauss_columns_eliminated']


def test_off_shell_global_gauge_ward_identity_needs_background_euler_contact():
    c=geometry(); a=fields(6); eta=np.array([.2,-.4,.3,.7])
    row=c['rows'][0]
    full={k:v.copy() for k,v in a.items()}
    for name,coefficient in [('gauge',row['connection_lambda'].value-1),
            ('gauge_tau',row['lambda_tau'].value),('gauge_rho',row['lambda_rho'].value)]:
        full[name][...,2:,:] += coefficient*M
    tangent={k:bracket(v,eta) for k,v in full.items()}
    second={k:bracket(v,eta) for k,v in tangent.items()}
    first=full_maxwell_weak_geometric_jets(c,[1.],np.ones(3)/3,**a,**indexed(tangent))
    curvature=hessian(c,a,tangent,tangent)
    background=full_maxwell_weak_geometric_jets(c,[1.],np.ones(3)/3,**a,**indexed(second))
    assert abs(first['weak']['values'][0])<2e-14
    assert abs(background['weak']['values'][0])>.01
    assert abs(curvature['value']+background['weak']['values'][0])<3e-14
    assert abs(curvature['curvature_contact'])>.01


def test_geometry_first_second_and_weak_mixed_derivatives_match_literal_action():
    a,v=fields(7),fields(8);c=geometry();weights=np.ones(3)/3
    result=full_maxwell_action_jet(c,[1.],weights,**a)
    weak=full_maxwell_weak_geometric_jets(c,[1.],weights,**a,**indexed(v))['weak']
    h=2e-4
    f=lambda x,y:literal_action(geometry(x,y),a)
    grad=np.array([(f(h,0)-f(-h,0))/(2*h),(f(0,h)-f(0,-h))/(2*h)])
    Hxy=(f(h,h)-f(h,-h)-f(-h,h)+f(-h,-h))/(4*h*h)
    np.testing.assert_allclose(result['gradient'],grad,rtol=2e-7,atol=1e-6)
    assert result['hessian'][0,1]==pytest.approx(Hxy,rel=3e-7,abs=2e-6)
    def W(x,y):
        return full_maxwell_weak_geometric_jets(geometry(x,y),[1.],weights,**a,**indexed(v))['weak']['values'][0]
    Wxy=(W(h,h)-W(h,-h)-W(-h,h)+W(-h,-h))/(4*h*h)
    assert weak['geometric_hessians'][0,0,1]==pytest.approx(Wxy,rel=3e-6,abs=2e-6)


def test_canonical_contacts_have_At_Ar_orientation_from_ftr_literal_action():
    c=geometry();a=fields(9);shape=a['gauge'].shape
    # Isolate tests for Ar and At; spatial test values vanish.
    v=np.zeros((1,2,3,5,4));v[0,0,:,1,0]=1;v[0,1,:,0,0]=1
    result=full_maxwell_weak_geometric_jets(c,[1.],np.ones(3)/3,**a,
        tests=v,tests_tau=np.zeros_like(v),tests_rho=np.zeros_like(v),
        tests_angular=np.zeros((1,2,3,3,5,4)))
    X=a['gauge_tau'][0,:,1]-a['gauge_rho'][0,:,0]+bracket(a['gauge'][0,:,0],a['gauge'][0,:,1])
    p=c['rows'][0]['electric_radial'].value*np.mean(X[:,0])
    np.testing.assert_allclose(result['temporal_momentum_test']['values'],[p,0],atol=1e-15)
    np.testing.assert_allclose(result['radial_momentum_test']['values'],[0,-p],atol=1e-15)


def test_actual_full_reference_spatial_block_agrees_with_existing_action_and_all_gauss_values_are_derived_zero():
    actual=retained_full_background_application(points=24,test_order=1)
    c=actual['coefficient_jets'];r=len(actual['rho']);count=2
    from bhsm.interface.muon_parent_retarded_hypercharge import regular_radial_basis
    H,Hr=regular_radial_basis(actual['rho'],1)
    tests=H[:,:,None,None,None]*M;tr=Hr[:,:,None,None,None]*M
    zero=np.zeros((r,1,3,4))
    old=spatial_maxwell_weak_geometric_jets(c,actual['quadrature'],[1.],
        gauge=zero,gauge_tau=zero,gauge_rho=zero,gauge_angular=np.zeros((r,1,3,3,4)),
        tests=tests,tests_tau=np.zeros_like(tests),tests_rho=tr,
        tests_angular=np.zeros((r,count,1,3,3,4)))
    values=actual['application']['weak']['values'].reshape(2,5,4)
    np.testing.assert_array_equal(values[:,:2],0)
    reconstructed=np.sqrt(8)*sum(values[:,i+2,i] for i in range(3))
    np.testing.assert_allclose(reconstructed,old['weak']['values'],rtol=5e-14,atol=1e-9)
    G=actual['application']['weak']['geometric_jacobian'].reshape(2,5,4,100)
    oldG=old['weak']['geometric_jacobian']
    np.testing.assert_allclose(np.sqrt(8)*sum(G[:,i+2,i] for i in range(3)),oldG,rtol=3e-13,atol=3e-8)
    assert np.linalg.norm(values[:,2:])>1
    assert actual['Gauss_zero_provenance'].startswith('At/Ar constant-angular tests: Ftr=0')
    assert not actual['stationary_E1_claim']


@pytest.mark.parametrize('bad',['complex','missing_derivative','double_volume','mixed_density'])
def test_rejects_mixed_or_silently_projected_action_operands(bad):
    c=geometry();a=fields(10);hw=np.ones(3)/3
    if bad=='complex':a['gauge']=a['gauge'].astype(complex)
    if bad=='missing_derivative':a['gauge_angular']=a['gauge_angular'][...,:4,:]
    if bad=='double_volume':hw=hw*(2*np.pi**2)
    if bad=='mixed_density':c['rows'][0]['electric_radial']=2*c['rows'][0]['electric_radial']
    with pytest.raises(ValueError):
        full_maxwell_action_jet(c,[1.],hw,**a)
