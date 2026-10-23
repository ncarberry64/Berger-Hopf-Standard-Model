import numpy as np
from bhsm.interface.muon_holomorphic_magnetic_source_faces import signed_field_face_source_complete,actual_owner_one_sided_source_germ
from bhsm.interface.muon_holomorphic_magnetic_birth_matching import signed_field_face_reconstruction


def test_whole_source_face_At_rate_first_matches_literal_independent_difference():
    rng=np.random.default_rng(544);draw=lambda s:rng.normal(size=s)+.1j*rng.normal(size=s)
    n,na=6,2;nd=n-na;f={q:draw((n,n))for q in('K','M','B_forward','B_reverse')};d={q:draw((1,n,n))for q in f}
    f['K'][:na,:na]+=4*np.eye(na);f['M'][na:,na:]+=5*np.eye(nd)
    for a in(f['M'],d['M'][0]):a[:na]=0;a[:,:na]=0
    for a in(f['B_forward'],d['B_forward'][0]):a[:,:na]=0
    for a in(f['B_reverse'],d['B_reverse'][0]):a[:na]=0
    S=np.eye(n);L=draw((n,2));w=[draw((2,3))for _ in range(3)];dw=[draw((1,2,3))for _ in range(3)];z=draw((2*nd,3));dz=draw((1,2*nd,3))
    base=signed_field_face_reconstruction(f,S,L,w,z,na);a=signed_field_face_source_complete(f,d,S,L,w,dw,dz,base,na)
    h=1e-5;branches=[signed_field_face_reconstruction({q:v+t*d[q][0]for q,v in f.items()},S,L,
        [x+t*y[0]for x,y in zip(w,dw)],z+t*dz[0],na)for t in(h,-h)]
    fd=(branches[0]['total_coordinate_rate']-branches[1]['total_coordinate_rate'])/(2*h)
    np.testing.assert_allclose(a['total_coordinate_rate_first'][0],fd,rtol=4e-9,atol=4e-8)
    assert np.linalg.norm(a['total_coordinate_rate_first'][0,:na])>1
    np.testing.assert_allclose(a['original_time_Gauss_and_momentum_first_rows'],0,atol=2e-14)


def test_one_sided_second_source_is_not_inferred_from_C1_value_rate():
    sources=[dict(Q=np.array([q]),Q_coordinate_time=np.array([v]))for q,v in((1+.1j,.2j),(2+.3j,.3),(4+.2j,-.1j))]
    knots=np.array([0,.5,1]);left=actual_owner_one_sided_source_germ(.5,knots,sources,.03,side='left')
    right=actual_owner_one_sided_source_germ(.5,knots,sources,.03,side='right')
    np.testing.assert_array_equal(left[0],right[0]);np.testing.assert_array_equal(left[1],right[1])
    assert np.linalg.norm(left[2]-right[2])>1e4
