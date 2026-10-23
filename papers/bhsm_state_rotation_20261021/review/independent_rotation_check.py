"""Independent sign/ordering checks; synthetic controls, no physical state selection.

This uses an analytic rotating tide and a direct matrix solve. It does not
duplicate the inherited R1 propagator or assert a microscopic correspondence.
"""
import json
import sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp, quad

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code'))
from rotation_response import wedge_matrix, finite_map, skew_coefficient


class AnalyticProvider:
    def __init__(self, K):
        self.K = K
        self.normalization = 1 / (np.sqrt(2) * K)  # c=1, synthetic control
    def chi_of_z(self, z):
        return z
    def S(self, t):
        return np.sin(np.sqrt(self.K) * np.asarray(t)) / np.sqrt(self.K)
    def weyl_rows(self, t):
        return np.array([1., t, 0., 0., 0., 0.])


def main():
    u, v = np.eye(6)[:2]
    p = AnalyticProvider(.3)
    B, G, _ = wedge_matrix(p, 0., 1., rtol=1e-12, atol=1e-17, max_step=.003)
    # Independent nested scalar quadrature of the explicit determinant u-v.
    ordered = quad(lambda t: p.S(1-t) * quad(
        lambda r: p.S(t-r)*p.S(r)*(r-t), 0., t,
        epsabs=1e-14, epsrel=1e-12)[0], 0., 1.,
        epsabs=1e-14, epsrel=1e-12)[0] / p.S(1.)
    checks = []
    for e in [.04, .02, .01]:
        even = (skew_coefficient(finite_map(p,0.,1.,u,v,e)) +
                skew_coefficient(finite_map(p,0.,1.,u,v,-e))) / (2*e*e)
        checks.append({'amplitude':e, 'even_skew_over_amplitude_squared':even,
                       'absolute_error':abs(even-ordered)})
    flat = AnalyticProvider(1e-8)
    Bflat, _, _ = wedge_matrix(flat, 0., 1., max_step=.003)
    # Flat D''=-eps (Z+tX)D gives skew(D)_2=-J/360 exactly.
    flat_limit = -1/360
    # Wronskian tests optical reciprocity/twist, not symmetry of D itself.
    Z = np.diag([1.,-1.]); X = np.array([[0.,1.],[1.,0.]])
    def rhs(t,s):
        D,V=s[:4].reshape(2,2),s[4:].reshape(2,2)
        return np.r_[V.ravel(),(-(.3*np.eye(2)+.2*(Z+t*X))@D).ravel()]
    s=solve_ivp(rhs,(0,1),np.r_[np.zeros(4),np.eye(2).ravel()],
                method='DOP853',rtol=1e-13,atol=1e-15,max_step=.003).y[:,-1]
    D,V=s[:4].reshape(2,2),s[4:].reshape(2,2)
    wronskian=V.T@D-D.T@V
    result={'status':'INTERNAL_INDEPENDENT_SYNTHETIC_CHECK',
            'ordered_double_integral':ordered, 'response_B01':float(B[0,1]),
            'ordered_integral_absolute_error':float(abs(B[0,1]-ordered)),
            'matrix_skew_error':float(np.max(abs(B+B.T))),
            'finite_matrix_ode_checks':checks,
            'near_flat_B01':float(Bflat[0,1]),'flat_exact_value':flat_limit,
            'near_flat_limit_absolute_error':float(abs(Bflat[0,1]-flat_limit)),
            'finite_nonsymmetric_D_skew':skew_coefficient(D),
            'finite_wronskian_max_abs':float(np.max(abs(wronskian)))}
    assert result['ordered_integral_absolute_error'] < 2e-12
    assert result['matrix_skew_error'] < 1e-14
    assert result['near_flat_limit_absolute_error'] < 1e-10
    assert checks[-1]['absolute_error'] < 2e-9
    assert result['finite_wronskian_max_abs'] < 1e-12
    (ROOT/'review'/'independent_rotation_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
