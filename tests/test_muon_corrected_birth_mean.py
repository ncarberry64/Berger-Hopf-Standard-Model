"""Algebraic fixtures verify the new action application, not physical fields."""
import numpy as np
from bhsm.interface import muon_corrected_birth_mean as owner


def test_endpoint_constitutive_reconstructs_velocity_and_gauss(monkeypatch):
    rng=np.random.default_rng(108);mass=np.zeros((488,488));mass[80:480,80:480]=np.diag(np.linspace(1,2,400))
    mixed=np.zeros_like(mass);mixed[80:,80:]=rng.normal(size=(408,408))*.01
    mixed[:80,80:]=rng.normal(size=(80,408))*.01
    stiffness=np.eye(488);stiffness[:80,80:]=rng.normal(size=(80,408))*.01;stiffness[80:,:80]=stiffness[:80,80:].T
    from bhsm.interface.muon_parent_maxwell_full_retarded import constrained_gauss_schur
    reduced=constrained_gauss_schur(mass,mixed,stiffness,80)
    q=rng.normal(size=(400,8));q[:160]=0;qt=q*.13
    source=dict(connection_source=q,connection_source_rate=qt)
    monkeypatch.setattr(owner,'uniform_magnetic_source_first_jets',lambda *a,**kw:source)
    monkeypatch.setattr(owner,'corrected_profile_reached_sample',lambda *a,**kw:dict(reduced=reduced,raw_forms=(mass,mixed,stiffness)))
    rep=dict(rho=np.array([.2,.7]))
    state=rng.normal(size=(800,8))
    result=owner.endpoint_first_fields(np.zeros(268),rep,{},state,electric_charge=1.,nu_squared_action=4.)
    assert np.max(abs(result['Legendre_residual']))<3e-15
    assert np.max(abs(result['Gauss_residual']))<3e-15
    assert not np.allclose(result['velocity'],state[400:])
    assert result['algebraic_At_rate_used'] is False
    assert result['fields']['first_H_rate'].shape==(3,4,20)


def test_six_port_source_matches_saddle_perturbation_with_algebraic_contact():
    rng=np.random.default_rng(134);n=8;dim=18
    A=np.diag(np.arange(1.,9.));B=np.eye(8)[:6];C=np.eye(8)[6:]
    G=np.r_[B,C];K=np.block([[A,G.T],[G,np.zeros((8,8))]])
    rhs=np.r_[np.zeros((8,6)),np.eye(6),np.zeros((2,6))]
    sol=np.linalg.solve(K,rhs);theta=rng.normal(size=8)
    vi=np.arange(8);yi=np.arange(8,10)
    h=rng.normal(size=(dim,dim));h=(h+h.T)/2
    dtheta=rng.normal(size=8)
    chart=dict(master_count=9,v_indices=vi,y_indices=yi)
    base=dict(saddle=K,constrained_trace_lift=sol[:8],saddle_solution=sol,temporal_face_cotangent=theta)
    dg=lambda d,step:(h@d)[:,None,None]
    result=owner.six_port_mean_source(base,chart,np.zeros((dim,1,1)),dtheta[:,None,None],dg,
        difference_step=1e-5,coordinate_weights=np.ones(dim))
    dG=np.r_[np.zeros_like(B),h[np.ix_(yi,vi)]]
    dK=np.block([[h[np.ix_(vi,vi)],dG.T],[dG,np.zeros((8,8))]])
    eps=1e-5
    plus=(theta+eps*dtheta)@np.linalg.solve(K+eps*dK,rhs)[:8]
    minus=(theta-eps*dtheta)@np.linalg.solve(K-eps*dK,rhs)[:8]
    expected=(plus-minus)/(2*eps)
    np.testing.assert_allclose(result['six_source'][:,0,0],expected,rtol=2e-9,atol=2e-9)
    assert np.linalg.norm(result['saddle_contact'])>0
    assert np.max(abs(result['adjoint_residual']))<2e-15
    assert result['exact_stored_saddle_Lyy'] is False
