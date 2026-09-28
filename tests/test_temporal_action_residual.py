from pathlib import Path
import sys
import mpmath as mp
from flint import arb, arb_mat, ctx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from bhsm.interface.temporal_action_residual import descriptor_euler_residual, temporal_source


def test_descriptor_residual_matches_direct_equation_even_off_fiber_and_off_shell():
    ctx.prec = 384
    H = arb_mat([[2, 1], [1, 3]])
    dH = arb_mat([[1, -1], [-1, 2]])
    p = arb_mat([[1], [2]]); dp = arb_mat([[3], [-1]])
    h = arb_mat([[4], [1]]); dh = arb_mat([[-2], [3]])
    rhs = arb_mat([[2], [-1]]); drhs = arb_mat([[3], [5]])
    lam, dl, s, ds, b, db, N, dN = map(arb, ['.3', '.2', '.4', '-.1', '2', '3', '5', '2'])
    re = H*p-lam*p; dre = dH*p+H*dp-dl*p-lam*dp
    rh = H*h-lam*h+b*p-rhs
    drh = dH*h+H*dh-dl*h-lam*dh+db*p+b*dp-drhs
    a = descriptor_euler_residual(s=s,lam=lam,b=b,psi=p,hard=h,norm=N,
        eigen_residual=re,hard_residual=rh,ds=arb_mat([[ds]]),dlam=arb_mat([[dl]]),
        db=arb_mat([[db]]),dpsi=dp,dhard=dh,dnorm=arb_mat([[dN]]),
        deigen_residual=dre,dhard_residual=drh)
    G = b*p+s*h; dG = db*p+b*dp+ds*h+s*dh
    direct = (H*G-s*rhs)/N
    derivative = (dH*G+H*dG-ds*rhs-s*drhs-direct*dN)/N
    assert all(v.contains(0) for v in (a['value']-direct).entries())
    assert all(v.contains(0) for v in (a['first']-derivative).entries())


def test_event_limit_has_no_descriptor_division():
    ctx.prec = 256
    z = arb_mat(2, 1)
    a = descriptor_euler_residual(s=0,lam=0,b=1,psi=arb_mat([[1],[0]]),
        hard=arb_mat([[0],[3]]),norm=1,eigen_residual=z,hard_residual=z,
        ds=arb_mat([[1]]),dlam=arb_mat([[1]]),db=arb_mat([[2]]),
        dpsi=z,dhard=z,dnorm=arb_mat([[3]]),deigen_residual=z,dhard_residual=z)
    assert all(v.is_zero() for v in a['value'].entries()+a['first'].entries())


def test_temporal_integration_by_parts_with_moving_clock_and_multiplier():
    # Actual scalar action L=(v^2-q^2)/2+m*q on r in [0,1].
    # q=a+b*r+c*r^2, t=T*r, m=d+e*r, so v=q'/T.
    # Neither Euler nor multiplier equations are assumed to vanish.
    ctx.prec = 384
    with mp.workdps(80):
        def action(eps):
            a,b,c,T,d,e=[mp.mpf(s) for s in ('1','.2','.3','2','.4','-.1')]
            a+=eps; b-=2*eps; T+=3*eps; d+=4*eps
            return mp.quad(lambda r:T*((b+2*c*r)**2/(2*T*T)-(a+b*r+c*r*r)**2/2
                                        +(d+e*r)*(a+b*r+c*r*r)),[0,1])
        def endpoint(r):
            q=1+mp.mpf('.2')*r+mp.mpf('.3')*r*r
            v=(mp.mpf('.2')+mp.mpf('.6')*r)/2; m=mp.mpf('.4')-mp.mpf('.1')*r
            L=v*v/2-q*q/2+m*q
            return v*(1-2*r)+(L-v*v)*3*r
        def integrand(r):
            q=1+mp.mpf('.2')*r+mp.mpf('.3')*r*r
            v=(mp.mpf('.2')+mp.mpf('.6')*r)/2; m=mp.mpf('.4')-mp.mpf('.1')*r
            # E = pi'-nu L_q, where pi=v and nu=2.
            E=mp.mpf('.3')-2*(-q+m)
            return -E*(1-2*r)+2*q*4+(E*v+mp.mpf('.1')*q)*3*r
        truth=mp.diff(action,0)
        assert abs(truth-(endpoint(1)-endpoint(0)+mp.quad(integrand,[0,1])))<mp.mpf('1e-70')
        # Exact Boole integration (degree <=5) of the executable source for
        # this polynomial path, including the moving-time contribution.
        integral=arb(0)
        for i,w in enumerate([7,32,12,32,7]):
            r=arb(i)/4;q=1+arb('.2')*r+arb('.3')*r*r
            v=(arb('.2')+arb('.6')*r)/2;m=arb('.4')-arb('.1')*r
            E=arb('.3')-2*(-q+m)
            src=temporal_source(qdim=1,euler_residual=arb_mat([[E],[0]]),
                deuler_residual=arb_mat(2,1),multiplier_gradient=arb_mat([[q]]),
                multiplier_gradient_first=arb_mat(1,1),velocity=arb_mat([[v]]),
                velocity_first=arb_mat(1,1),multiplier_arc_rate=arb_mat([['-.1']]),
                multiplier_arc_first=arb_mat(1,1),clock=2,clock_first=arb_mat(1,1))
            integral+=arb(w)/90*(src['state'][0,0]*(1-2*r)+src['state'][2,0]*4+src['time'][0,0]*3*r)
        expected=arb(mp.nstr(truth-endpoint(1)+endpoint(0),75))+arb(0,arb('1e-74'))
        assert integral.overlaps(expected)
    # Separately bind the executable source signs on an exact point.
    z=arb_mat(1,1)
    out=temporal_source(qdim=1,euler_residual=arb_mat([[2],[7]]),
        deuler_residual=arb_mat([[3],[4]]),multiplier_gradient=arb_mat([[5]]),
        multiplier_gradient_first=arb_mat([[6]]),velocity=arb_mat([[7]]),
        velocity_first=arb_mat([[8]]),multiplier_arc_rate=arb_mat([[9]]),
        multiplier_arc_first=arb_mat([[10]]),clock=11,clock_first=arb_mat([[12]]))
    assert out['state'][0,0]==-2 and out['state'][1,0]==0 and out['state'][2,0]==55
    assert out['time'][0,0]==-31
    assert out['time_first'][0,0]==3*7+2*8-6*9-5*10
