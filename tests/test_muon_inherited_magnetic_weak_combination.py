"""Independent complex canonical source/metric and corner-return controls."""
import numpy as np
from bhsm.interface.muon_inherited_magnetic_weak_combination import combine_inherited_magnetic_weak_action


def _application(beta=0j):
    forms=[];first=[]
    for j in range(2):
        f=dict(K=np.diag([0.,2.+.3j]), M=np.diag([1.,1.+j]),
            B_forward=np.diag([0.,-.2+.4j]), B_reverse=np.diag([0.,-.2+.4j]))
        df=dict(K=np.diag([0.,.3j]),M=np.diag([0.,.2-.1j]),
            B_forward=np.diag([0.,.1j]),B_reverse=np.diag([0.,.1j]))
        forms.append({n:f[n]+beta*df[n] for n in f})
        first.append({n:df[n][None] for n in df})
    def face(t,j):
        wall=(1.+.4j*t)**2; d=t+.2j*t*t
        q=np.array([[1.+.3*t],[wall+beta*d]],complex)
        qt=np.array([[.3],[.8j*(1.+.4j*t)+beta*(1.+.4j*t)]],complex)
        qtt=np.array([[0.],[-.32+.4j*beta]],complex)
        dq=np.array([[[0.],[d]]]);dqt=np.array([[[0.],[1.+.4j*t]]]);dqtt=np.array([[[0.],[.4j]]])
        f=forms[j];df={n:first[j][n][0] for n in f}
        p=f['M']@qt+f['B_reverse']@q
        dp=df['M']@qt+f['M']@dqt[0]+df['B_reverse']@q+f['B_reverse']@dq[0]
        force=f['K']@q+f['B_forward']@qt; pdot=f['M']@qtt+f['B_reverse']@qt
        e=force-pdot
        de=df['K']@q+f['K']@dq[0]+df['B_forward']@qt+f['B_forward']@dqt[0]-df['M']@qtt-f['M']@dqtt[0]-df['B_reverse']@qt-f['B_reverse']@dqt[0]
        return dict(total_field=q,total_coordinate_rate=qt,total_field_first=dq,total_coordinate_rate_first=dqt,
            canonical_momentum=p,canonical_momentum_first=dp[None],original_action_force=force,
            original_unbordered_Euler_rows=e,original_first_reconstructed_rows=np.zeros((1,2,1),complex),
            wall_and_frame_reactions_first=de[None,1:])
    x,w=np.polynomial.legendre.leggauss(5);points=[]
    for j in range(2):
        for a,b in zip(x,w):
            t=.5*j+.25*(a+1)
            points.append(dict(face(t,j),cell=j,scale=-.25j*b))
    p={n:np.array([a[n] for a in points]) for n in points[0]}
    return combine_inherited_magnetic_weak_action(forms,first,p,face(0,0),face(1,1),face(.5,0),face(.5,1),np.array([[0.,1.]]))


def test_literal_source_metric_and_coefficient_corner_close_original_action():
    r=_application()
    np.testing.assert_allclose(r['original_bulk_minus_complete_weak_return'],0,atol=8e-16)
    np.testing.assert_allclose(r['original_bulk_first_minus_complete_weak_return_first'],0,atol=8e-16)
    assert np.linalg.norm(r['coefficient_corner_return'])>.1
    assert np.linalg.norm(r['coefficient_corner_return_first'])>.1
    assert np.linalg.norm(r['integrated']['wall_force_work'])>.1


def test_independent_complex_differentiation_of_complete_bulk_and_returns():
    h=2e-6*(1.+.3j);r=_application();plus=_application(h);minus=_application(-h)
    fd=(plus['integrated']['base_total']-minus['integrated']['base_total'])/(2*h)
    np.testing.assert_allclose(fd,r['integrated']['total_first_total'][0],rtol=2e-9,atol=2e-10)
    np.testing.assert_allclose((plus['complete_weak_return']-minus['complete_weak_return'])/(2*h),
        r['complete_weak_return_first'][0],rtol=2e-9,atol=2e-10)
    assert abs(fd.imag).max()>.01
