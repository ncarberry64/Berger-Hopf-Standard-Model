"""Product/contact checks for saved-response event consumption."""
import numpy as np
import pytest

from bhsm.interface.muon_d5_event_response_combination import (
    tied_normal_amplitudes, assemble_wall_combination, reconstruct_combination,
    event_matching_rows, event_representation_error_transport,
)


def test_normal_amplitude_derivative_uses_common_g_and_four_independent_profiles():
    rng=np.random.default_rng(911)
    g=rng.normal(size=(3,18,2))+1j*rng.normal(size=(3,18,2))
    gx=g*(.07+.03j)
    names=('right_plus','right_minus','left_plus','left_minus')
    p={name:np.array([.7,1.1,.9])+j*.13 for j,name in enumerate(names)}
    px={name:np.array([.02,-.03,.01])*(j+1) for j,name in enumerate(names)}
    pl=np.diag(np.r_[np.ones(12),np.zeros(6)]);pr=np.eye(18)-pl
    def call(eps):
        return tied_normal_amplitudes(g+eps*gx,gx,
            **{k:p[k]+eps*px[k] for k in names},
            **{k+'_source':px[k] for k in names},left_projector=pl,right_projector=pr)
    a,ax=call(0.)
    for slot in a:
        np.testing.assert_allclose((call(1e-6)[0][slot]-call(-1e-6)[0][slot])/2e-6,
            ax[slot],atol=6e-10,rtol=2e-8)
    np.testing.assert_allclose(a['a_LR']*p['left_plus'][:,None,None],g,atol=5e-16)
    np.testing.assert_allclose(a['a_RL']*p['left_minus'][:,None,None],g,atol=5e-16)
    assert np.max(abs(a['a_LR']-a['a_RL']))>.1
    p['left_plus'][1]=0
    with pytest.raises(ValueError):call(0.)


def _wall_fixture():
    rng=np.random.default_rng(36);n,na,k=3,2,2
    arrays=dict(times=np.array([-1.,-.4,0.]),amplitude_times=np.array([-1.,0.]))
    for side in ('plus','minus'):
        for suffix in ('','_source'):
            arrays['wall_'+side+'_complement_basis'+suffix]=rng.normal(size=(n,384,366))*.03
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        arrays[label+'_wall']=rng.normal(size=(n,384,18*na))*.03
        arrays[label+'_wall_source']=rng.normal(size=(n,384,18*na))*.01
    a={key:rng.normal(size=(na,18,k)) for key in ('a_R','a_LR','a_RL')}
    ax={key:rng.normal(size=(na,18,k))*.1 for key in a}
    h=rng.normal(size=(n,366,k));hx=rng.normal(size=h.shape)*.2
    return arrays,a,ax,h,hx


def test_wall_application_retains_all_h_coordinates_and_all_product_sources():
    arrays,a,ax,h,hx=_wall_fixture()
    def call(eps):
        changed={key:value.copy() for key,value in arrays.items()}
        for key in arrays:
            if key.endswith('_source'):continue
            source=key+'_source'
            if source in arrays:changed[key]=arrays[key]+eps*arrays[source]
        return assemble_wall_combination(changed,'minus',
            {key:a[key]+eps*ax[key] for key in a},ax,
            homogeneous=h+eps*hx,homogeneous_source=hx)
    result=call(0.)
    np.testing.assert_allclose((call(1e-6)['wall']-call(-1e-6)['wall'])/2e-6,
        result['wall_source'],atol=1e-9,rtol=1e-8)
    np.testing.assert_allclose(result['wall'],result['particular_wall']+result['homogeneous_wall'])
    # Every coordinate is consumed, including the last retained column.
    h2=h.copy();h2[:,-1]+=3
    changed=assemble_wall_combination(arrays,'minus',a,ax,homogeneous=h2,homogeneous_source=hx)
    np.testing.assert_allclose(changed['wall']-result['wall'],
        np.broadcast_to(arrays['wall_minus_complement_basis'][:,:,-1,None]*3,
            changed['wall'].shape),atol=7e-16)
    assert result['homogeneous_coordinates_selected'] is False
    with pytest.raises(ValueError):
        assemble_wall_combination(arrays,'minus',a,ax,homogeneous=h[:,:365],homogeneous_source=hx[:,:365])


def _identity_factor_arrays(times):
    n=len(times);order=3;d=64
    arrays=dict(times=times,radial_nodes=np.array([1.,.99]),
        radial_boundaries=np.array([1.,.99]),radial_order=np.array(order))
    for branch in ('particle','conjugate'):
        prefix='minus_'+branch+'_';arrays[prefix+'block_count']=np.array(1)
        prefix+='block0_';arrays[prefix+'indices']=np.arange(d)
        arrays[prefix+'initial']=np.eye(n*d,dtype=complex)[None]
        arrays[prefix+'initial_source']=np.zeros((1,n*d,n*d),complex)
        arrays[prefix+'slopes']=np.zeros((1,order,n*d,n*d),complex)
        arrays[prefix+'slopes_source']=np.zeros((1,order,n*d,n*d),complex)
    return arrays


def test_reconstruction_applies_existing_full_factors_without_boundary_selection():
    times=np.array([-1.,-.4,0.]);arrays=_identity_factor_arrays(times)
    rng=np.random.default_rng(811)
    base=rng.normal(size=(384,2));slope=rng.normal(size=base.shape)
    wall=base[None]+times[:,None,None]*slope[None]
    source=wall*.23j;points=np.array([-.83,-.19]);radii=np.array([.998,.993])
    result=reconstruct_combination(arrays,'minus',wall,source,times=points,radii=radii)
    expected=base[None]+points[:,None,None]*slope[None]
    np.testing.assert_allclose(result['value'],np.broadcast_to(expected,result['value'].shape),atol=2e-15)
    np.testing.assert_allclose(result['time'],np.broadcast_to(slope,result['time'].shape),atol=3e-15)
    np.testing.assert_allclose(result['source'],result['value']*.23j,atol=4e-16)
    assert np.max(abs(result['radial']))==0
    assert np.count_nonzero(np.sum(abs(result['value'])**2,axis=(0,1,3)))==384


def _contact_scope():
    return dict(frame='included in explicit trace and transfer sources',
        density='included in explicit trace sources',
        normal_profile='included in explicit trace sources',
        child_evaluation='total child derivative; total base variation includes DF_B delta x_child once')


def test_event_jacobi_includes_base_gradient_and_child_evaluation_exactly_once():
    rng=np.random.default_rng(144)
    p=rng.normal(size=(2,4,3));px=rng.normal(size=p.shape)*.11
    grad=rng.normal(size=(2,2,4,3));f=rng.normal(size=(2,2))*.07
    c=rng.normal(size=(2,5,3));cx=rng.normal(size=c.shape)*.2
    u=rng.normal(size=(2,5,4));ux=rng.normal(size=u.shape)*.03
    result=event_matching_rows(c,cx,p,px,grad,transfer=u,
        transfer_source=ux,total_base_source=f,trace_contact_scope=_contact_scope())
    def row(eps):
        # The explicit shifted parent evaluation is not copied into px.
        parent=p+eps*px+eps*np.einsum('pa,padk->pdk',f,grad)
        return c+eps*cx-(u+eps*ux)@parent
    np.testing.assert_allclose((row(1e-6)-row(-1e-6))/2e-6,
        result['event_source_rows'],atol=5e-10,rtol=1e-8)
    assert np.linalg.norm(result['base_pullback_contact'])>.1
    assert np.linalg.norm(result['bundle_transfer_contact'])>.1
    assert result['moving_child_evaluation_appended_again'] is False
    with pytest.raises(ValueError):
        event_matching_rows(c,cx,p,px,grad,transfer=u,transfer_source=ux,
            total_base_source=f,trace_contact_scope={})


def test_finite_error_transport_is_exact_signed_difference_and_absolute_majorant():
    rng=np.random.default_rng(44)
    def random(shape):return rng.normal(size=shape)+1j*rng.normal(size=shape)
    c,cx,p,px,g=(random(shape)*.001 for shape in ((2,5,3),(2,5,3),(2,4,3),(2,4,3),(2,2,4,3)))
    u=random((2,5,4));ux=random(u.shape)*.07;f=random((2,2))*.1
    result=event_representation_error_transport(c,cx,p,px,g,transfer=u,
        transfer_source=ux,total_base_source=f,operand_scope='finite_representation_difference')
    np.testing.assert_allclose(result['event_rows'],c-u@p)
    assert np.all(abs(result['event_rows'])<=result['event_absolute_budget']+1e-17)
    assert np.all(abs(result['event_source_rows'])<=result['event_source_absolute_budget']+1e-17)
    assert result['strong_residual_identified_as_trace_error'] is False
    assert result['continuum_error_bound'] is False
    with pytest.raises(ValueError):
        event_representation_error_transport(c,cx,p,px,g,transfer=u,
            transfer_source=ux,total_base_source=f,operand_scope='strong_residual_as_error')
