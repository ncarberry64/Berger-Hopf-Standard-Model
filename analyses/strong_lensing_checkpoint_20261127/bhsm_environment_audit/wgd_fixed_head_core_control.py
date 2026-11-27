"""Conditional fixed-head/core, fixed mass axisymmetric source counterexample."""
import json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from pathlib import Path

rows = []
for eps in [-0.2, 0., 0.2]:
    b_over_R = .5
    y = brentq(lambda z: z+eps*z**3-b_over_R, 0., 1.)
    cut = float(np.sqrt(1-y*y))
    fraction = 1-cut
    def r(x):
        return 1+eps*(1-x*x)
    def projected_radius(x):
        return r(x)*np.sqrt(max(0, 1-x*x))
    quadrature = quad(lambda x: float(projected_radius(x) <= b_over_R), 0, 1, points=[cut], epsabs=1e-13)[0]
    q2 = quad(lambda x:r(x)**2*(3*x*x-1)/2,0,1,epsabs=1e-13)[0]
    q2_exact = -4*eps/15-16*eps**2/105
    assert abs(quadrature-fraction) < 2.e-13
    assert abs(q2-q2_exact) < 2.e-13
    assert r(-1) == r(1) == 1
    rows.append(dict(eps=eps,R_head_over_R=1,R_tail_over_R=1,R_lateral_over_R=float(r(0)),M_cyl_over_M=float(fraction),M_fraction_quadrature=quadrature,Q2_over_MR2=q2,weak_field_on_axis_deflection_over_4GM_c2b=float(fraction)))
record = dict(scope="Axisymmetric weak-field source witness only. Not BHSM solution, observation, relativistic shock shape, or galaxy fit.", reference="Center is a declared regular-side core-reference proxy; no coordinate or metric assigned to the abstract core.", r_over_R="1 + eps sin(theta)^2", aperture_over_R=.5, rows=rows, extreme_fraction_ratio=rows[0]['M_cyl_over_M']/rows[-1]['M_cyl_over_M'])
Path(__file__).with_suffix('.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
