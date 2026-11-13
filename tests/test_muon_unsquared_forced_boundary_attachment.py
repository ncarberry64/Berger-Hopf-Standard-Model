import numpy as np
from bhsm.interface.muon_unsquared_forced_boundary_attachment import (
    unsquared_boundary_source_two_jet, attached_current_two_jet,
    source_corrected_unsquared_return,
)


def test_attached_energy_magnetic_jets_match_whole_noncommuting_boundary_action():
    rng=np.random.default_rng(3407)
    shapes=((3,3),(3,2),(3,3),(3,3),(3,2),(2,3),(2,3),(2,2))
    keys=('trace','source_return','initial_boundary','final_boundary',
          'boundary_source','initial_target','final_target','direct_current')
    draw=lambda scale:{k:scale*(rng.normal(size=s)+1j*rng.normal(size=s))
                       for k,s in zip(keys,shapes)}
    base,energy,magnetic,mixed=draw(.3),draw(.2),draw(.2),draw(.1)
    base['initial_boundary']+=4*np.eye(3)
    a=unsquared_boundary_source_two_jet(base,(energy,magnetic),mixed)
    answer=attached_current_two_jet(a)
    def independent(e,b):
        p={k:base[k]+e*energy[k]+b*magnetic[k]+e*b*mixed[k] for k in keys}
        U,r,Bi,Bf,source,Li,Lf,direct=(p[k]for k in keys)
        x=np.linalg.solve(Bi+Bf@U,source-Bf@r)
        return direct+Li@x+Lf@(U@x+r)
    h=2e-5
    np.testing.assert_allclose(answer['current_first'][0],
        (independent(h,0)-independent(-h,0))/(2*h),rtol=8e-9,atol=3e-10)
    h=2e-4
    np.testing.assert_allclose(answer['current_mixed'],
        (independent(h,h)-independent(h,-h)-independent(-h,h)+independent(-h,-h))/(4*h*h),
        rtol=2e-7,atol=3e-9)
    np.testing.assert_allclose(answer['current'],answer['independent_transpose_current'],atol=1e-16)
    np.testing.assert_allclose(answer['current_first'],answer['first_transpose_current'],atol=2e-16)
    np.testing.assert_allclose(answer['mixed_original_rows'],0,atol=2e-16)
    assert np.linalg.norm(a['forced_boundary_source']-base['boundary_source'])>.1


def test_square_range_forced_face_and_energy_source_contacts_are_counted_once():
    rng=np.random.default_rng(78)
    draw=lambda shape:.2*(rng.normal(size=shape)+1j*rng.normal(size=shape))
    P=4*np.eye(4)+draw((4,4));dP=draw((4,4))
    sharp=3*np.eye(4)+draw((4,4));dsharp=draw((4,4))
    rangeK=draw((4,4));rangeB=draw((4,2))
    R,L=draw((4,2)),draw((2,4));dR,dL=draw((4,2)),draw((2,4))
    def values(s):
        p,ps,r,l=P+s*dP,sharp+s*dsharp,R+s*dR,L+s*dL
        K=ps@p+rangeK;b=ps@r+rangeB
        n=np.linalg.solve(K,b);c=np.zeros_like(n);c[:2]=np.linalg.solve(K[:2,:2],b[:2])
        return p,r,l,K,b,n,c
    _,_,_,K,b,xN,xD=values(0)
    dK=dsharp@P+sharp@dP;db=dsharp@R+sharp@dR
    dxN=np.linalg.solve(K,db-dK@xN);dxD=np.zeros_like(xD)
    dxD[:2]=np.linalg.solve(K[:2,:2],(db-dK@xD)[:2])
    blocks=lambda a:(np.array([a[:2,:2],a[2:,2:]]),a[None,:2,2:],a[None,2:,:2])
    a=source_corrected_unsquared_return(blocks(P),R.reshape(2,2,2),L.reshape(2,2,2).transpose(1,0,2),
        xN.reshape(2,2,2),xD.reshape(2,2,2),weak_factor_first=blocks(dP),
        right_moments_first=dR.reshape(2,2,2),literal_left_first=dL.reshape(2,2,2).transpose(1,0,2),
        natural_square_response_first=dxN.reshape(2,2,2),core_square_response_first=dxD.reshape(2,2,2))
    # Native square derivative-image contacts are nonzero in this control.
    assert np.linalg.norm(a['natural_range_source'])>.01
    np.testing.assert_allclose(a['core_square_current'],a['original_current_with_core_source_return'],atol=2e-17)
    np.testing.assert_allclose(a['forced_boundary_current'],a['independent_forced_boundary_current'],atol=2e-17)
    np.testing.assert_allclose(a['forced_boundary_current_first'],a['independent_forced_boundary_current_first'],atol=2e-17)
    h=2e-5
    vp,vm=values(h),values(-h)
    direct=((vp[2]@(vp[5]-vp[6]))-(vm[2]@(vm[5]-vm[6])))/(2*h)
    np.testing.assert_allclose(a['forced_boundary_current_first'],direct,rtol=1e-9,atol=2e-12)
    np.testing.assert_allclose(a['forced_original_source_first_identity'],0,atol=2e-16)
