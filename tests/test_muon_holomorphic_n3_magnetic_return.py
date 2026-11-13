import numpy as np

from bhsm.interface.muon_holomorphic_n3_magnetic_return import (
    source_n3_return_angular_images, projected_magnetic_return_action,
)
from bhsm.interface.muon_holomorphic_n1_magnetic_operands import signed_n1_magnetic_point_operands
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from test_muon_holomorphic_n1_magnetic_operands import _fixture, _literal_action


def _named_tests(binding):
    # The fixture's fourth original radial profile is the unit wall lift.
    ids=binding['value_permutation']
    T=np.eye(84)[:,[int(np.flatnonzero(ids==j)[0])for j in range(60,84)]]
    np.testing.assert_allclose(np.r_[binding['lifts']['W'],binding['lifts']['hv']]@T,np.eye(24),atol=0)
    return T


def test_projection_before_assembly_equals_complete_owned_n1_action():
    rng,b,Ee,Eo,G,*_=_fixture();T=_named_tests(b)
    f=.025*(rng.normal(size=(336,3))+.4j*rng.normal(size=(336,3)));ft=.017*f
    full=signed_n1_magnetic_point_operands(b,f,ft,Ee,Eo,Eo,G)
    projected=projected_magnetic_return_action(b,f,ft,T,Ee,Eo,Eo,G)
    Je=np.kron(T,np.eye(10));Jo=np.kron(T,np.eye(4))
    for n in ('K','B_forward','B_reverse','M'):
        np.testing.assert_allclose(projected['delta_'+n],Je.T@full['delta_'+n]@Jo,rtol=5e-14,atol=3e-15)
    assert not projected['physical_current_or_Green_or_loop_or_pole_selected']


def test_complete_n3_source_returns_match_literal_complex_action_and_reverse():
    rng,b,*_=_fixture();T=_named_tests(b);a=source_n3_return_angular_images()
    angular=scalar_s3_discretization(4);labels=angular['real_basis_labels'];Y=angular['real_basis_values'];w=angular['haar_weights']
    ids={n:np.flatnonzero([l[0]==n for l in labels])for n in (1,2,3,4)}
    f=.035*(rng.normal(size=(336,3))+.4j*rng.normal(size=(336,3)));ft=.02*f
    draw=lambda n:.02*(rng.normal(size=n)+.4j*rng.normal(size=n))
    assert a['complete_n3_times_n1_image_residual']<5e-14
    n4_action=0.
    for n in (2,4):
        E=a['derivatives'];G=a['gaunts'][n]
        z=projected_magnetic_return_action(b,f,ft,T,E[n],E[3],E[1],G)
        reverse=projected_magnetic_return_action(b,f,ft,T,E[3],E[n],E[1],G.transpose(1,0,2))
        for key,opposite in (('K','K'),('B_forward','B_reverse'),('B_reverse','B_forward'),('M','M')):
            np.testing.assert_allclose(reverse['delta_'+key],z['delta_'+opposite].transpose(0,2,1),rtol=4e-13,atol=2e-14)
        ev,et,ov,ot=draw(24*len(ids[n])),draw(24*len(ids[n])),draw(384),draw(384)
        predicted=ev@z['delta_K'][0]@ov+ev@z['delta_B_forward'][0]@ot
        predicted+=et@z['delta_B_reverse'][0]@ov+et@z['delta_M'][0]@ot
        lift=lambda v,degree:np.kron(T,np.eye(len(ids[degree])))@v
        actual=0j
        for s in (-1,1):
            for e in (-1,1):
                for o in (-1,1):
                    actual+=s*e*o*_literal_action(b,(Y[:,ids[1]],Y[:,ids[n]],Y[:,ids[3]]),(E[1],E[n],E[3]),w,
                        ((s*f[:,0],s*ft[:,0]),(e*lift(ev,n),e*lift(et,n)),(o*lift(ov,3),o*lift(ot,3))))/8
        np.testing.assert_allclose(predicted,actual,rtol=3e-8,atol=5e-14)
        if n==4:n4_action=np.linalg.norm(z['delta_K'])
    assert n4_action>1e-4
