import numpy as np
from bhsm.interface.muon_corrected_birth_source_endpoint import (
    corrected_birth_endpoint_source, endpoint_formal_area_offset,
)
from bhsm.interface.muon_coupled_phase_trace_projection import (
    coupled_phase_trace_projection, coupled_phase_trace_parameter,
)
from bhsm.interface.aether_full_reset_action_jacobian import (
    _attachment_jacobian_at_order, _symmetric_power,
)


def _groups():
    sizes = [('incoming_constraints',40), ('child_constraints',40),
        ('incoming_energy',1), ('child_energy',1), ('gauge_trace',64),
        ('gauge_temporal_dual',64), ('Higgs_trace',4), ('Higgs_temporal_dual',4),
        ('moving_geometric_trace',4), ('normal_position_trace',1),
        ('common_attachment_temporal_dual',2), ('common_normal_temporal_dual',1)]
    out={}; i=0
    for key,n in sizes:out[key]=list(range(i,i+n));i+=n
    assert i==226
    return out


def _fixture():
    rng=np.random.default_rng(30995)
    H=np.diag(2+.05j+np.arange(504)/1000).astype(complex)
    H+=rng.normal(size=H.shape)*.0004+1j*rng.normal(size=H.shape)*.0001
    H=(H+H.T)/2
    Hp=H[:252,:252].copy()+.3*np.eye(252)
    vi=np.r_[np.arange(106,212),np.arange(358,464)]
    yi=np.r_[np.arange(212,252),np.arange(464,504)]
    areaG=rng.normal(size=504)*.03+.02j*rng.normal(size=504)
    areaH=np.diag(.07+.02j+np.arange(504)/10000)
    tf=-H[vi].copy();tf[:106,:252]+=2*Hp[106:212]
    at=-areaG[vi].copy();at[:106]+=2*areaG[106:212]
    a=dict(hessian=H,parent=dict(hessian=Hp),velocity_indices=vi,algebraic_indices=yi,
        area_gradient_per_gamma=areaG,area_Hessian_per_gamma=areaH,
        temporal_cotangent=rng.normal(size=212)+.2j*rng.normal(size=212),
        temporal_cotangent_first=tf,area_temporal_cotangent_per_gamma=at)
    return rng,dict(action=a,groups=_groups(),area_parameter_source=rng.normal(size=226)+.1j*rng.normal(size=226))


def test_complete_signed_own_joint_duals_and_endpoint_roles_keep_both_terms():
    rng,base=_fixture();a=base['action']
    J=rng.normal(size=(226,504))*.1+.04j*rng.normal(size=(226,504))
    dh=rng.normal(size=504)+.3j*rng.normal(size=504);dl=dh*1e-16
    T=rng.normal(size=(6,504))*.03+.01j*rng.normal(size=(6,504))
    app=corrected_birth_endpoint_source(base,J,dh,dl,T,parameter_amplitude=1)
    z=app['arrays'];d=dh+dl
    pi=a['hessian'][a['velocity_indices']]@d+a['area_gradient_per_gamma'][a['velocity_indices']]
    own=a['parent']['hessian'][106:212]@d[:252]+a['area_gradient_per_gamma'][106:212]
    expected=np.r_[2*own-pi[:106],-pi[106:]]
    np.testing.assert_allclose(z['temporal_dual_response_high']+z['temporal_dual_response_low'],expected,atol=4e-15)
    np.testing.assert_allclose(z['original226_response_high']+z['original226_response_low'],
        J@d+base['area_parameter_source'],atol=2e-14)
    assert np.linalg.norm(expected-np.r_[own,-pi[106:]])>1
    assert app['temporal_dual_decomposition_difference_upper']<2e-14
    assert len(app['role_response_uppers'])==3
    assert not app['analytic_direction_or_dual_conjugated']
    assert app['normal_natural_force_not_forced_zero']
    assert app['child_reconstituted_source_gradient_not_appended_to_joint_action']
    assert np.linalg.norm(z['temporal_dual_response_low'])>0


def test_area_offset_reprojects_full_phase_before_inverse():
    rng,base=_fixture();a=base['action'];phase=np.r_[a['velocity_indices'],a['algebraic_indices']]
    E=rng.normal(size=(6,292))*.03+.01j*rng.normal(size=(6,292))
    F=np.eye(292)[-4:];common=np.zeros((6,3));common[[0,2],0]=1;common[[1,3],1]=1;common[[4,5],2]=1
    p=coupled_phase_trace_projection(a['hessian'][np.ix_(phase,phase)],E,F,
        np.r_[a['temporal_cotangent'],np.zeros(80)],common)
    area=coupled_phase_trace_parameter(p,a['area_Hessian_per_gamma'][np.ix_(phase,phase)],
        np.r_[a['area_temporal_cotangent_per_gamma'],np.zeros(80)])
    normalization=np.zeros(37);B=_attachment_jacobian_at_order(12,normalization);bn=_symmetric_power(B@B.T,.5)
    ai=base['groups']['common_attachment_temporal_dual'];ni=base['groups']['common_normal_temporal_dual']
    base['projection']=p;base['residual']=rng.normal(size=226).astype(complex)
    base['residual'][ai]=bn@p['common_trace_cotangent'][:2];base['residual'][ni]=p['common_trace_cotangent'][2]
    base['area_parameter_source'][ai]=bn@area['common_trace_cotangent_parameter'][:2]
    base['area_parameter_source'][ni]=area['common_trace_cotangent_parameter'][2]
    step=2e-5
    plus=endpoint_formal_area_offset(base,step,normalization)
    minus=endpoint_formal_area_offset(base,-step,normalization)
    fd=(plus['residual']-minus['residual'])/(2*step)
    np.testing.assert_allclose(fd,base['area_parameter_source'],atol=3e-8,rtol=2e-8)
    assert np.linalg.norm(plus['projection']['phase_lift']-p['phase_lift'])>1e-7
    assert not plus['physical_tension_selected']
