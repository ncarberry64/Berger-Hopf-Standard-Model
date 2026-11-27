import json
from pathlib import Path
import numpy as np
p=Path(__file__).parent
j=json.loads((p/'he0435_joint_projected.json').read_text())
def m(v): return np.linalg.norm(v[:,None]-v,axis=2).max()
good=[]
for r in j['runs']:
    assert r['minimum_principal_eigenvalue']>0
    assert r['converged']==(r['last_max_scaled_residual']<2e-7)
    for d in r['LOS_half_length_Mpc'].values():
        x,y,z=[np.asarray(d[k+'_sources_arcsec']) for k in ('ordinary','joint','isolated')]
        for v,k in [(x,'ordinary'),(y,'joint_R1'),(z,'isolated_R1')]:
            assert abs(np.sqrt(np.mean(np.sum((v-v.mean(0))**2,axis=1)))-d[k+'_common_source_RMS_arcsec'])<1e-13
        assert abs(m(y-z)*1e6-d['joint_minus_isolated_after_G1_pairwise_source_shift_microarcsec'])<1e-8
        assert abs(m(y-x)*1e3-d['joint_vs_ordinary_pairwise_differential_source_shift_mas'])<1e-11
        assert d['rear_propagation_increment_on_that_differential_microarcsec']<0.02
    if r['converged']:
        good.append(r['LOS_half_length_Mpc']['0.8']['joint_minus_isolated_after_G1_pairwise_source_shift_microarcsec'])
assert len(good)==4
assert 4.65<min(good)<4.67 and 4.80<max(good)<4.82
print(f'5 run diagnostics, 20 ray maps; 4 accepted, 1 tolerance miss; joint effect {min(good):.6f}–{max(good):.6f} μas')
