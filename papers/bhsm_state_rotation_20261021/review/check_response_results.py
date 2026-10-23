"""Scientific acceptance checks, separate from implementation construction."""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
j=json.loads((ROOT/'results/rotation_response.json').read_text())
for r in j['segments']:
    B=np.array(r['B'])
    assert np.max(abs(B+B.T))<1e-20
    assert np.all(np.isfinite(B))
assert len(j['all_coordinate_pairs_at_z1'])==15
assert j['quadrature_error_omega']<1e-25
assert j['refined_omega_difference']<1e-24
assert max(x['absolute_coefficient_error'] for x in j['finite_ode_checks'])<1e-24
assert abs(j['common_profile_finite_rotation'])<1e-18
assert abs(j['swap_state_omega2']+j['segments'][1]['omega2'])<1e-24
assert j['admissibility']['min_reduced_kinetic_eigenvalue']>0
assert max(j['admissibility']['sampled_global_potential_bound_Phi_Psi'])<.001
assert j['strong_lens']['finite_difference_absolute_error']<1e-13
assert abs(j['strong_lens']['Fermat_weighted_jacobian_skew_first_order'])<1e-18
assert j['provider_audit']['physical_anchor_reconstruction_max_abs']<1e-12
assert j['provider_audit']['original_constraint_scaled_max_abs']<1e-8
# The original quoted example is checked from recovered, immutable results.
old=ROOT.parent/'bhsm_angular_lensing_20261021'
text=(old/'README.md').read_text(encoding='utf8')
assert '-0.353216090' in text and '7.753621449' in text
print('PASS: antisymmetry, ordered quadrature, refinement, direct ODE, common-profile null,')
print('state-swap sign, finite-domain kinetic gate, weak potentials, lens symmetrizer, original example.')
