import numpy as np

from bhsm.interface.muon_common_higgs_seam_insertion import (
    full_higgs_seam_numerator_jet,common_higgs_seam_maps,
    apply_intrinsic_common_higgs_seam,fixed_intrinsic_higgs_vertices)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_holomorphic_d5_trace_action import principal_normal_point_trace
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def test_ambient_normal_factors_and_jets_match_original_trace_owner():
    full=full_d5_localized_lepton_trace();H=np.array([.13,.71,-.09,.07]);Ht=np.array([.03,-.02,.04,.01])
    U,Ut,rho,rhot=.17,-.031,1.23,.091
    seam=full_higgs_seam_numerator_jet(H,Ht,U,Ut,rho,rhot,full_representation=full)
    # These nonunit independent analytic values are algebraic controls, not
    # values assigned to the actual real muon normal profile.
    nr={'plus':(1.7+.1j,1.3-.2j,.021-.011j,-.013+.007j),
        'minus':(.9-.03j,1.4+.08j,-.017+.002j,.019-.005j)}
    tr={}
    for label,eps in(('plus',1),('minus',-1)):
        ur,ul,urt,ult=nr[label]
        tr[label]=principal_normal_point_trace(ur,ul,np.array([urt]),np.array([ult]),U,np.array([Ut]),
            sheet_orientation=eps,full_representation=full)
    recovered=np.zeros((18,18),complex);recoveredt=recovered.copy()
    for label,ch in seam['channels'].items():
        l,r=ch['left_sheet'],ch['right_sheet'];A,B=ch['left_chiral_projector'],ch['right_chiral_projector']
        C=tr[l]['normalized_Dirac_bar_left_Gamma0'];Ct=tr[l]['normalized_Dirac_bar_left_Gamma0_first'][0]
        D=tr[r]['normalized_right_Gamma0'];Dt=tr[r]['normalized_right_Gamma0_first'][0]
        M,Mt=seam['background_intrinsic_mass'],seam['background_intrinsic_mass_time']
        direct=-rho*C@A@M@B@D
        directt=-rhot*C@A@M@B@D-rho*(Ct@A@M@B@D+C@A@Mt@B@D+C@A@M@B@Dt)
        ur,_,urt,_=nr[r];_,ul,_,ult=nr[l];alpha=1/(ul*ur);alphat=-alpha*(ult/ul+urt/ur)
        np.testing.assert_allclose(alpha*ch['ambient_background_numerator'],direct,rtol=8e-15,atol=2e-17)
        np.testing.assert_allclose(alpha*ch['ambient_background_numerator_time']+alphat*ch['ambient_background_numerator'],directt,rtol=2e-14,atol=2e-17)
        EL=tr[l]['normal_mode_Dirac_bar_left_point_lift'];ELt=tr[l]['normal_mode_Dirac_bar_left_point_lift_first'][0]
        ER=tr[r]['normal_mode_right_point_lift'];ERt=tr[r]['normal_mode_right_point_lift_first'][0]
        recovered+=EL@direct@ER
        recoveredt+=ELt@direct@ER+EL@directt@ER+EL@direct@ERt
    np.testing.assert_allclose(recovered,-rho*seam['background_intrinsic_mass'],rtol=1e-14,atol=3e-17)
    np.testing.assert_allclose(recoveredt,-rhot*seam['background_intrinsic_mass']-rho*seam['background_intrinsic_mass_time'],rtol=3e-14,atol=4e-17)


def test_common_Higgs_maps_retain_independent_complex_source_and_full_Hdot():
    H=np.array([.13,.71,-.09,.07]);Ht=np.array([.03,-.02,.04,.01])
    t=np.array([.77,-.11,.23,-.19,.17,.31]);rad=np.array([[.71,.2,-.1],[.83,-.3,.4]])
    hs=common_higgs_seam_maps(H,Ht,t,rad);T=higgs_u2_real_representation()['real_generators']
    rng=np.random.default_rng(701);z=rng.normal(size=1200)+1j*rng.normal(size=1200)
    expected=t[0]*z[1120:].reshape(4,20);expectedt=t[1]*z[1120:].reshape(4,20)
    for i in range(2):
        for j in range(2):
            a=z[800+160*i+80*j:880+160*i+80*j].reshape(4,20)
            eta=rad[j,0]*t[2+2*i]*a;etat=rad[j,0]*t[3+2*i]*a
            expected-=np.einsum('cij,j,ch->ih',T,H,eta)
            expectedt-=np.einsum('cij,j,ch->ih',T,H,etat)+np.einsum('cij,j,ch->ih',T,Ht,eta)
    np.testing.assert_allclose((hs['value']@z).reshape(4,20),expected,rtol=3e-15,atol=2e-15)
    np.testing.assert_allclose((hs['time']@z).reshape(4,20),expectedt,rtol=3e-15,atol=2e-15)
    assert np.count_nonzero(hs['value'][:,:800])==0


def test_intrinsic_common_operator_is_complex_linear_without_Hermitian_source_projection():
    V=fixed_intrinsic_higgs_vertices();M=np.zeros((80,1200));M[:,1120:]=np.eye(80)
    z=np.zeros(1200,complex);z[1120]=1j
    gaunt=np.eye(20)[:,:,None];u=np.ones((18,1,2),complex)
    result=apply_intrinsic_common_higgs_seam(z,M,V,gaunt,u)
    np.testing.assert_allclose(result[:,0],1j*V[0]@u[:,0],rtol=0,atol=0)
    assert np.linalg.norm(result)>0
    # Fixed real-basis conjugate vertex is multiplied by the SAME i.
    np.testing.assert_allclose((1j*V[0]).conj().T,-1j*V[0],rtol=0,atol=0)
