"""Source fields and all7 map contacts checked in original nonlinear rows."""
import numpy as np
from scipy.linalg import expm
from bhsm.interface.muon_d5_joint_map_source_application import apply_joint_map_sources
from bhsm.interface.muon_d5_joint_connection_higgs_value import joint_value_rows_jacobian
from bhsm.interface.muon_d5_spatial_bundle_application import cross_matrix,rotation_su2
from bhsm.interface.muon_d5_higgs_temporal_bundle_application import real_higgs,complex_higgs


def test_source_particular_and_all_free_contacts_satisfy_original_equation_derivatives():
    rng=np.random.default_rng(141)
    O=expm(cross_matrix([.2,-.3,.1]));R=expm(cross_matrix([-.1,.2,.3]));K=rotation_su2(R);U=np.exp(.3j)*K
    Ap=rng.normal(size=(5,4));Ac=rng.normal(size=(5,4));Ac[2:]=np.c_[O.T@Ap[2:,:3]@R.T,O.T@Ap[2:,3]]
    Apx=rng.normal(size=(5,4));Acx=rng.normal(size=(5,4))
    hp=np.array([.3+.2j,.8-.1j]);hc=U@hp
    hpx=rng.normal(size=2)+1j*rng.normal(size=2);hcx=rng.normal(size=2)+1j*rng.normal(size=2)
    def co(a,ax,h,hx):
        return dict(gauge_connection_material=a[None].astype(complex),
            gauge_connection_material_first=ax[None,None].astype(complex),
            intrinsic_H_realified=real_higgs(h),intrinsic_H_realified_first=real_higgs(hx)[None])
    joint=dict(initial_candidate_index=np.array([0]),base_rotation=O[None],gauge_rotation=R[None],
        gauge_SU2_lift=K[None],Higgs_middle=U[None],Higgs_unit_phase=np.array([np.exp(.3j)]))
    previous=dict(child_spatial_wall_trace_pivot=np.eye(12),child_spatial_wall_field_raw_indices=np.arange(168,180),
        child_raw_field_source_corrections=np.zeros((1,268)))
    a,r=apply_joint_map_sources(co(Ap,Apx,hp,hpx),co(Ac,Acx,hc,hcx),joint,previous,
        dict(child_Higgs_raw_source_corrections=np.zeros((1,268))),
        dict(material_clock_differential=np.array(.7),material_clock_differential_first=np.array(-.2)))
    delta=a['child_raw_field_Higgs_source_correction'][0]
    free=a['child_raw_field_Higgs_free_rotation_phase_coefficients'][0]
    eps=2e-6
    def rows(step,coordinate=None):
        d=delta if coordinate is None else free[:,coordinate]
        x=np.zeros(7) if coordinate is None else np.eye(7)[coordinate]*step
        pp=Ap+step*Apx if coordinate is None else Ap
        cc=Ac+step*Acx if coordinate is None else Ac
        cc=cc.copy();cc[2:]+=step*d[168:180].reshape(3,4)
        ph=hp+step*hpx if coordinate is None else hp
        ch=hc+step*hcx if coordinate is None else hc
        ch=ch+step*complex_higgs(d[260:264])
        return joint_value_rows_jacobian(pp[2:],cc[2:],ph,ch,O,R,U,x)[0]
    np.testing.assert_allclose((rows(eps)-rows(-eps))/(2*eps),0,atol=2e-10)
    for i in range(7):
        np.testing.assert_allclose((rows(eps,i)-rows(-eps,i))/(2*eps),0,atol=3e-10)
    assert r['candidates'][0]['source_before_max']>1
    assert r['candidates'][0]['source_after_max']<2e-16
    assert r['physical_admission'] is False
