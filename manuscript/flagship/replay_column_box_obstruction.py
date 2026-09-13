"""Replay the supplied Cartesian-box obstruction, not physical noncontraction."""
from fractions import Fraction as F
import json
from pathlib import Path

source = Path(__file__).resolve().parent/'generated/column_box_obstruction.json'
data = json.loads(source.read_text())
result, operands = data['result'], data['operands']
if result['physical_map_noncontraction_proved'] or not result['requires_independent_output_coordinate_box_interpretation']:
    raise ValueError('The required conditional claim boundary changed')
a = list(map(F, operands['axis_node_14_exact']))
rL, rT = map(F, operands['trial_radii_exact'])
j, k = result['trial_column'], result['box_coordinate']
assert len(a) == 74 and j == 14 and k == 73 and 0 < rT < rL
s = sum(v*v for v in a)
ell = rT*a[j]/s
t = [rT*(F(i == j)-v*a[j]/s) for i, v in enumerate(a)]
assert sum(a[i]*t[i] for i in range(74)) == 0
assert all(a[i]*ell+t[i] == rT*F(i == j) for i in range(74))
assert abs(ell) < rL and sum(v*v for v in t) <= rT*rT
rho = F(result['saved_coordinate_radius_exact'])
assert rho > 0
qk = [F(i == k)-a[i]*a[k] for i in range(74)]
gain_squared = rho*rho*sum(v*v for v in qk)
assert gain_squared == F(result['projected_box_gain_squared_exact'])
lower = F(result['projected_box_gain_lower_exact'])
assert lower > 1 and lower*lower <= gain_squared < (lower+F(1, 10**12))**2
assert 1-lower == F(result['relaxed_contraction_margin_upper_exact'])
print('Exact Cartesian-box obstruction replay passed; physical noncontraction is not claimed.')
