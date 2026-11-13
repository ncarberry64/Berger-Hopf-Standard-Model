import numpy as np
from bhsm.interface.muon_holomorphic_n1_magnetic_quadratic_action import signed_magnetic_quadratic_source_motion


def test_whole_nonsymmetric_signed_quadratic_derivative_has_both_independent_slots():
    rng=np.random.default_rng(11931);draw=lambda shape:rng.normal(size=shape)+.7j*rng.normal(size=shape)
    names=('K','B_forward','B_reverse','M');F={n:draw((7,7))for n in names};dF={n:draw((2,7,7))for n in names}
    f,ft=draw((7,3)),draw((7,3));df,dft=draw((2,7,3)),draw((2,7,3))
    a=signed_magnetic_quadratic_source_motion(F,dF,f,ft,df,dft)
    def action(s,t):
        ff,tt=f+t*df[s],ft+t*dft[s];m={n:F[n]+t*dF[n][s]for n in names}
        return .5*(ff.T@m['K']@ff+ff.T@m['B_forward']@tt+tt.T@m['B_reverse']@ff+tt.T@m['M']@tt)
    for s in range(2):
        # Central FD of the whole action is independent of helper placement
        # assembly and preserves non-Hermitian/complex duals.
        fd=(action(s,1e-5)-action(s,-1e-5))/(2e-5)
        np.testing.assert_allclose(a['total_first_total'][s],fd,rtol=3e-9,atol=3e-8)
    assert np.linalg.norm(a['left_response_motion_total']-a['right_response_motion_total'])>1
    assert np.linalg.norm(a['coefficient_motion_M'])>1
    z=signed_magnetic_quadratic_source_motion(F,{n:1j*v for n,v in dF.items()},f,ft,1j*df,1j*dft)
    np.testing.assert_allclose(z['total_first_total'],1j*a['total_first_total'],rtol=2e-14,atol=2e-13)
