import numpy as np
from itertools import combinations
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_complex_coupled_reset_continuation import central_reset_Ward_rows
from bhsm.interface.muon_trace_enriched_charged_current_response import enriched_central_profiles
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def test_two_central_identities_reconstruct_all_original_dependent_rows():
    phase,_=retained_input('outgoing',{});rep=phase['representation'];coordinates=phase['coordinates']
    labels=rep['gauge_labels'];At=[j for j,i in enumerate(coordinates['At_indices'])if labels[i]['internal']==3]
    Ar=[j for j,i in enumerate(coordinates['dynamic_gauge_indices'])if labels[i]['field']=='A_rho'and labels[i]['internal']==3]
    profiles=enriched_central_profiles(rep);theta=profiles['theta_coefficients'];D=profiles['radial_derivative_coefficients']
    wall=rep['wall_trace_map'][0,3,np.array(coordinates['At_indices'])[At]]@theta
    T=higgs_u2_real_representation()['real_generators'][3]
    Hp=np.array([.2+.1j,-.3+.4j,.5-.2j,.1+.3j]);Hc=np.array([.4-.2j,.1+.2j,-.2+.1j,.6-.3j])
    pp=np.array([.1+.2j,-.4+.3j,.7-.1j,.2+.5j]);pc=np.array([-.2+.1j,.5-.4j,.3+.6j,-.1-.2j])
    ap=np.array([.3+.1j,-.2+.4j,.5-.6j,.2+.3j]);ac=np.array([-.1+.2j,.4-.3j,.2+.1j,-.5+.2j])
    pair=max(combinations(range(4),2),key=lambda ids:abs(np.linalg.det(theta[list(ids)].T)))
    gp=np.zeros(4,complex);gc=gp.copy()
    gp[list(pair)]=np.linalg.solve(theta[list(pair)].T,-D.T@ap+wall*((T@Hp)@pp))
    gc[list(pair)]=np.linalg.solve(theta[list(pair)].T,-D.T@ac+wall*((T@Hc)@pc))
    groups=dict(incoming_constraints=list(range(40)),child_constraints=list(range(40,80)),
        gauge_trace=list(range(80,144)),gauge_temporal_dual=list(range(144,208)),
        Higgs_trace=list(range(208,212)),Higgs_temporal_dual=list(range(212,216)))
    r=np.zeros(226,complex);r[np.array(groups['incoming_constraints'])[24+np.array(At)]]=gp
    r[np.array(groups['child_constraints'])[24+np.array(At)]]=gc
    r[np.array(groups['gauge_temporal_dual'])[Ar]]=ap-ac
    r[groups['Higgs_trace']]=Hc-Hp;r[groups['Higgs_temporal_dual']]=pp-pc
    temporal=np.zeros(212,complex);temporal[208:212]=-pc
    raw=np.zeros((2,268),complex);raw[0,260:264]=Hp;raw[1,260:264]=Hc
    application=dict(groups=groups,residual=r,action=dict(temporal_cotangent=temporal,
        constant_profile_child=dict(coordinates=coordinates)))
    control=central_reset_Ward_rows(application,raw,rep)
    np.testing.assert_allclose(control['original_nonlinear_identity'],0,atol=2e-15)
    dependent=control['dependent_original_rows'];keep=control['independent_original_rows'];L=control['rows']
    np.testing.assert_allclose(r[dependent],-np.linalg.solve(L[:,dependent],L[:,keep]@r[keep]),atol=2e-15)
    assert len(keep)==224 and np.linalg.norm(L.conj()@r)>.1
